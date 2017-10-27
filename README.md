# cosyhutch
Keeps the rabbit hutch cosy with a tube heater, temperature sensor and wireless socket relay.

`cosycron.py` is the main program that logs from the sensors and creates data log files.

## Testing
`cosycron.py` can be tested on mac OS (known as Darwin to python) due to the `if sys.platform == 'darwin':` conditionals. I found that crontab wasn't the best way to schedule a job on mac OS, so I used the `launchctl` daemon, thanks to [Alvin Alexander's article](https://alvinalexander.com/mac-os-x/mac-osx-startup-crontab-launchd-jobs). The file `com.rosedene.cosysimtest.plist` is symlinked into `/Users/Clive/Library/LaunchAgents` to achieve this. It works but needs fully qualified paths in the code to do so, hence the hardcoding of the logging configuration files. Not a big deal, the same thing happens on the pi.

Here are some important `launchctl` commands.

    launchctl load com.rosedene.cosysimtest.plist
    launchctl unload com.rosedene.cosysimtest.plist 
    launchctl unload /Users/Clive/Library/LaunchAgents/com.rosedene.cosysimtest.plist # after reboot

Remember to remove the symlink after testing!
