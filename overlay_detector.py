import win32gui
import win32con
import win32api
import win32process
import time
from datetime import datetime

def get_window_info(hwnd):
    """Get comprehensive window information."""
    try:
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        
        info = {
            'is_layered': bool(ex_style & win32con.WS_EX_LAYERED),
            'is_transparent': bool(ex_style & win32con.WS_EX_TRANSPARENT),
            'is_topmost': bool(ex_style & win32con.WS_EX_TOPMOST),
            'is_toolwindow': bool(ex_style & win32con.WS_EX_TOOLWINDOW),
            'has_caption': bool(style & win32con.WS_CAPTION),
            'alpha': None
        }
        
        # Only get alpha if window is actually layered
        if info['is_layered']:
            try:
                _, _, alpha = win32gui.GetLayeredWindowAttributes(hwnd)
                info['alpha'] = alpha
            except:
                # Some layered windows don't support GetLayeredWindowAttributes
                info['alpha'] = None
        
        return info
    except:
        return None

def is_likely_overlay(hwnd, title, class_name, width, height, info):
    """Determine if window is likely a suspicious overlay."""
    
    # Check for truly suspicious characteristics
    suspicious_score = 0
    reasons = []
    
    # CRITICAL: Transparent click-through is highly suspicious
    if info['is_transparent']:
        suspicious_score += 3
        reasons.append("Click-through transparency (WS_EX_TRANSPARENT)")
    
    # Layered window with actual transparency that's meaningful
    # Note: Many apps report alpha incorrectly, so we need strict criteria
    if info['is_layered'] and info['alpha'] is not None and info['alpha'] > 0:
        # Very low alpha (nearly invisible) with topmost is highly suspicious
        if info['alpha'] < 30 and info['is_topmost']:
            suspicious_score += 2
            reasons.append(f"Nearly invisible + topmost (alpha={info['alpha']})")
        # Moderately transparent, topmost, and no title
        elif 30 <= info['alpha'] < 200 and info['is_topmost'] and not title:
            suspicious_score += 1
            reasons.append(f"Transparent + topmost + no title (alpha={info['alpha']})")
    
    # Large window with no caption that's topmost (potential full-screen overlay)
    if info['is_topmost'] and not info['has_caption'] and width > 800 and height > 600:
        suspicious_score += 1
        reasons.append("Large topmost window without title bar")
    
    # Tool window that's transparent and topmost
    if info['is_toolwindow'] and info['is_topmost'] and info['is_layered']:
        suspicious_score += 1
        reasons.append("Topmost tool window with layered attribute")
    
    return suspicious_score >= 2, reasons

def detect_suspicious_overlays():
    """Detect windows that might be invisible overlays."""
    suspicious = []
    
    def enum_callback(hwnd, results):
        if not win32gui.IsWindowVisible(hwnd):
            return
        
        title = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        
        # Get window position and size
        try:
            rect = win32gui.GetWindowRect(hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
        except:
            return
        
        # Skip very small windows (likely UI elements)
        if width < 100 or height < 100:
            return
        
        info = get_window_info(hwnd)
        if not info:
            return
        
        # Check if this is a suspicious overlay
        is_suspicious, reasons = is_likely_overlay(hwnd, title, class_name, width, height, info)
        
        if is_suspicious:
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                process_handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
                process_name = win32process.GetModuleFileNameEx(process_handle, 0)
                win32api.CloseHandle(process_handle)
            except:
                pid = 0
                process_name = "Unknown"
            
            results.append({
                'hwnd': hwnd,
                'title': title or "(No title)",
                'class': class_name,
                'process': process_name,
                'alpha': info['alpha'],
                'topmost': info['is_topmost'],
                'transparent': info['is_transparent'],
                'layered': info['is_layered'],
                'size': f"{width}x{height}",
                'reasons': reasons,
                'pid': pid
            })
    
    win32gui.EnumWindows(enum_callback, suspicious)
    return suspicious

def monitor_overlays(interval=2):
    """Continuously monitor for suspicious overlays."""
    print("=" * 80)
    print("TRANSPARENT OVERLAY DETECTOR - Windows 11")
    print("=" * 80)
    print("Monitoring for suspicious windows with reduced false positives...")
    print("Press Ctrl+C to stop\n")
    
    last_count = 0
    
    try:
        while True:
            overlays = detect_suspicious_overlays()
            
            if overlays:
                if len(overlays) != last_count:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ⚠️  ALERT: {len(overlays)} suspicious overlay(s) detected!")
                    print("=" * 80)
                    
                    for i, overlay in enumerate(overlays, 1):
                        print(f"\n🚨 SUSPICIOUS WINDOW #{i}:")
                        print(f"  Title: {overlay['title']}")
                        print(f"  Class: {overlay['class']}")
                        print(f"  Process: {overlay['process']}")
                        print(f"  Size: {overlay['size']}")
                        print(f"  PID: {overlay['pid']}")
                        print(f"  Properties:")
                        print(f"    - Topmost: {overlay['topmost']}")
                        print(f"    - Transparent: {overlay['transparent']}")
                        print(f"    - Layered: {overlay['layered']}")
                        print(f"    - Alpha: {overlay['alpha']}")
                        print(f"  ⚠️  Reasons flagged:")
                        for reason in overlay['reasons']:
                            print(f"    • {reason}")
                    print("\n" + "=" * 80)
                    last_count = len(overlays)
                else:
                    # Overlay still present, just update timestamp
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Still detecting {len(overlays)} suspicious overlay(s)", end='\r')
            else:
                if last_count > 0:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ✓ All suspicious overlays cleared")
                    last_count = 0
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ No suspicious overlays detected", end='\r')
            
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")

if __name__ == "__main__":
    try:
        import win32process
    except ImportError:
        print("Error: pywin32 not installed")
        print("Install with: pip install pywin32")
        exit(1)
    
    monitor_overlays()