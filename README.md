This is a proof-of-concept. The solution detects transparent overlays like Cluely in Windows 11.

STEPS
1. Run overlay_detector.py from a Windows command shell. This is the detector which monitors for overlays.

2. Run test_overlay.py from another Windows command shell and create one or more overlays using the UI.

TODO
1. Adjust thresholds and add more suspicious patterns
2. Screenshot comparison analysis
3. GPU overlay detection
4. Network activity monitoring during screen shares
5. Process behavior analysis (injection/hooking detection)
6. Window z-order manipulation detection
