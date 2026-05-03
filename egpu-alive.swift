import Cocoa
import Metal
import MetalKit

class AppDelegate: NSObject, NSApplicationDelegate {
    var window: NSWindow!
    var mtkView: MTKView!
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        // Vega 56 explizit wählen
        var vegaDevice: MTLDevice?
        for device in MTLCopyAllDevices() {
            if device.isRemovable {
                vegaDevice = device
                break
            }
        }
        
        guard let device = vegaDevice else {
            print("Keine eGPU gefunden!")
            return
        }
        print("Nutze: \(device.name)")
        
        window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 1, height: 1),
            styleMask: [.borderless],
            backing: .buffered,
            defer: false
        )
        mtkView = MTKView(frame: window.contentRect(forFrameRect: window.frame), device: device)
        mtkView.clearColor = MTLClearColor(red: 0, green: 0, blue: 0, alpha: 1)
        mtkView.isPaused = false
        mtkView.enableSetNeedsDisplay = false
        mtkView.preferredFramesPerSecond = 1
        window.contentView = mtkView
        window.orderFront(nil)
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()