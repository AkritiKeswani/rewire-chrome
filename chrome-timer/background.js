var timeout;
var interval;

var setDate;
var pauseDate;
var alarmDate;

var greenColor = [76, 187, 23, 255];
var yellowColor = [250, 150, 0, 255];
var guiLagAdjustment = 500;

var alarmSound = new Audio("chime.mp3");

function setAlarm(tMillis)
{
    interval = tMillis;
    ringIn(tMillis + guiLagAdjustment);
}

function ringIn(tMillis)
{
    // Internal JS function with a call back
    clearTimeout(timeout);

    // Set blocking websites
    chrome.storage.local.set({"isBlockingEnabled" : true}, function() {
        console.log("Blocking enabled.");
    });

    pauseDate = null;

    var tSecs = parseInt(tMillis / 1000);
    var tMins = parseInt(tSecs / 60);
    var secs = tSecs % 60;
    var tHrs = parseInt(tMins / 60);
    var mins = tMins % 60;
    var millis = tMillis % 1000;

    alarmDate = new Date();
    // alarmDate.setTime(alarmDate.getTime() + millis);
    alarmDate.setHours(alarmDate.getHours() + tHrs);
    alarmDate.setMinutes(alarmDate.getMinutes() + mins);
    alarmDate.setSeconds(alarmDate.getSeconds() + secs);
    alarmDate.setMilliseconds(alarmDate.getMilliseconds() + millis);

    setDate = new Date();
    timeout = setTimeout(ring, alarmDate.getTime() - setDate.getTime());

    chrome.browserAction.setBadgeBackgroundColor({color:greenColor});
    setInterval(function() {
        chrome.browserAction.setBadgeText({text: getTimeLeftString()});
    }, 1000);
}

function pause()
{
    pauseDate = new Date();
    clearTimeout(timeout);
    chrome.browserAction.setBadgeBackgroundColor({color:yellowColor});
    // Set blocking websites
    chrome.storage.local.set({"isBlockingEnabled" : false}, function() {
        console.log("Blocking disabled.");
    });
}

function resume()
{
    var remainingAfterPause = (alarmDate.getTime() - pauseDate.getTime());
    ringIn(remainingAfterPause);
}

function restart()
{
    ringIn(interval + guiLagAdjustment);
}

function getTimeLeft()
{
    if (pauseDate)
        return (alarmDate.getTime() - pauseDate.getTime());

    var now = new Date();
    return (alarmDate.getTime() - now.getTime());
}

function getTimeLeftPercent()
{
    return parseInt(getTimeLeft() / interval * 100);
}

function getTimeLeftString()
{
    var until = getTimeLeft();
    var tSecs = parseInt(until / 1000);
    var tMins = parseInt(tSecs / 60);
    var secs = tSecs % 60;
    var tHrs = parseInt(tMins / 60);
    var mins = tMins % 60;
    if(secs < 10) secs = "0" + secs;
    if(mins < 10) mins = "0" + mins;
    if(tHrs < 10) tHrs = "0" + tHrs;
    return ((tHrs > 0 ? tHrs + ":" : "") + mins + ":" + secs);
}

function didCreateNotification(notificationId) {}

function ring()
{
    var options = {
        type: "basic",
        title: "Timer",
        message: "Time\'s up!",
        iconUrl: "img/48.png",
        priority: 2
    }
    chrome.notifications.create("", options, didCreateNotification);

    alarmSound.play();
    turnOff();
}

function turnOff()
{
    clearTimeout(timeout);
    interval = 0;
    alarmDate = null;
    pauseDate = null;
    setDate = null;
    chrome.browserAction.setBadgeText({text: ""});
    // Set blocking websites
    chrome.storage.local.set({"isBlockingEnabled" : false}, function() {
        console.log("Blocking disabled.");
    });
}

function error()
{
    alert("Please enter a number between 1 and 240.");
}
