@echo off

start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
--remote-debugging-port=9222 ^
--user-data-dir="C:\Users\ander\AppData\Local\Google\Chrome\User Data" ^
--profile-directory="Profile 18" ^
"https://business.facebook.com/latest/home"
