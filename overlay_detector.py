import win32gui
import win32con
import win32api
import time
from datetime import datetime

def get_window_transparency(hwnd):
    """Get the transparency/alpha value of a window."""
    try:
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        if ex_style & win32con.WS_EX_LAYERED:
            # Window uses layered attribute
            try:
                _, _, alpha = win32gui.GetLayeredWindowAttributes(hwnd)
                return alpha
            except:
                return None
    except:
        pass
    return 255  # Fully opaque

def is_window_topmost(hwnd):
    """Check if window has topmost flag."""
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    return bool(ex_style & win32con.WS_EX_TOPMOST)

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
        
        # Skip very small windows
        if width < 50 or height < 50:
            return
        
        alpha = get_window_transparency(hwnd)
        is_topmost = is_window_topmost(hwnd)
        
        # Detect suspicious characteristics
        suspicious_flags = []
        
        # Check for low opacity
        if alpha is not None and alpha < 50:
            suspicious_flags.append(f"Low opacity ({alpha})")
        
        # Check for topmost windows with no title
        if is_topmost and not title:
            suspicious_flags.append("Topmost + No title")
        
        # Check for layered windows
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        if ex_style & win32con.WS_EX_LAYERED:
            suspicious_flags.append("Layered window")
        
        # Check for transparent windows
        if ex_style & win32con.WS_EX_TRANSPARENT:
            suspicious_flags.append("Transparent click-through")
        
        if suspicious_flags:
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                process_name = "Unknown"
            except:
                pid = 0
                process_name = "Unknown"
            
            results.append({
                'hwnd': hwnd,
                'title': title or "(No title)",
                'class': class_name,
                'alpha': alpha,
                'topmost': is_topmost,
                'size': f"{width}x{height}",
                'flags': suspicious_flags,
                'pid': pid
            })
    
    win32gui.EnumWindows(enum_callback, suspicious)
    return suspicious

def monitor_overlays(interval=10):
    """Continuously monitor for suspicious overlays."""
    print("=" * 70)
    print("TRANSPARENT OVERLAY DETECTOR - Windows 11")
    print("=" * 70)
    print("Monitoring for suspicious windows...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            overlays = detect_suspicious_overlays()
            
            if overlays:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Found {len(overlays)} suspicious window(s):")
                print("-" * 70)
                
                for i, overlay in enumerate(overlays, 1):
                    print(f"\n#{i}:")
                    print(f"  Title: {overlay['title']}")
                    print(f"  Class: {overlay['class']}")
                    print(f"  Size: {overlay['size']}")
                    print(f"  Alpha: {overlay['alpha']}")
                    print(f"  Topmost: {overlay['topmost']}")
                    print(f"  PID: {overlay['pid']}")
                    print(f"  Suspicious flags: {', '.join(overlay['flags'])}")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] No suspicious overlays detected", end='\r')
            
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")

if __name__ == "__main__":
    # Note: Requires pywin32
    # Install with: pip install pywin32
    try:
        import win32process
    except ImportError:
        print("Error: pywin32 not installed")
        print("Install with: pip install pywin32")
        exit(1)
    
    monitor_overlays()