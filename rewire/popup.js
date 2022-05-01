var refreshDisplayTimeout;
var bgpage = chrome.extension.getBackgroundPage();
var previousValues = [30, 45, 60, 75];
var editing = false;
bgpage.isLoggedIn;

document.addEventListener('DOMContentLoaded', function () {
    load();
    document.querySelector('#start').addEventListener('click', setTimer);
    document.querySelector('#cancel').addEventListener('click', reset);
    document.querySelector('#wrench').addEventListener('click', swap);
    // document.querySelector('#pause').addEventListener('click', pauseTimer);
    document.querySelector('#resume').addEventListener('click', resumeTimer);
    // document.querySelector('#restart').addEventListener('click', restartTimer);
    document.querySelector('#loginSubmit').addEventListener('click', login);
    document.querySelector('#logout').addEventListener('click', logout);
});

function show(section)
{
    document.getElementById(section).style.display = "block";
}

function saveBlocklist(accessToken) {
    (async () => {
        const rawResponse = await fetch('https://ccd8-2a00-79e1-abc-c11-e86b-e81e-76cf-cef3.ngrok.io/authed/blocklist/get_blocked/', {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' +  accessToken
          }
        });
        const content = await rawResponse.json();

        const responseStatus = rawResponse.status;

        blocklist = []
        
        for (item of content) {
            blocklist.push(item.website);
        }

        chrome.storage.local.set({'blocklist' : blocklist}, function() {
            console.log("Blocklist set to = " + blocklist);
        });

    })();
}

function saveFriendlist(accessToken) {
    (async () => {
        const rawResponse = await fetch('https://ccd8-2a00-79e1-abc-c11-e86b-e81e-76cf-cef3.ngrok.io/authed/friend/get_friends/', {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' +  accessToken
          }
        });
        const content = await rawResponse.json();

        const responseStatus = rawResponse.status;

        friendlist = []

        console.log(content);
        
        var select = document.querySelector('#friend-list');

        for (var i = 1; i <= content.length; i++) {
            var opt = document.createElement('option');
            opt.value = content[i - 1].username;
            opt.innerHTML = `${content[i - 1].first_name} ${content[i - 1].last_name}`;
            select.appendChild(opt);
        }

    })();
}

function isVisible(section)
{
    return document.getElementById(section).style.display != "none";
}

function showInline(section)
{
    document.getElementById(section).style.display = "inline";
}

function hide(section)
{
    document.getElementById(section).style.display = "none";
}

function load()
{
    hide("settings");
    hide("modify");
    hide("resume");
    hide("login");
    editing = false;
    chrome.storage.local.get(['accessToken'], function(result) {
        saveBlocklist(result.accessToken);
        saveFriendlist(result.accessToken);
    });

    // if timer is paused, show resume button and hide pause button
    if(bgpage.pauseDate)
    {
        showInline("resume");
        hide("pause");
    }

    // loads custom times if they exist
    for(var i = 0; i < document.choices.radio.length; i++)
        if(localStorage[i] != null)
            document.getElementById("s"+i).textContent = localStorage[i];

    // if timer is off, show login and settings
    if(!bgpage.alarmDate)
    {
        if (bgpage.isLoggedIn) {
            show("settings");
            hide("display");
        }
        else {
            show("login");
            hide("display");
        }
    }

    // else, show countdown
    else
    {
        document.querySelector("#moneyOnLine").innerText = bgpage.accountabilityMoney;
        show("display");
        refreshDisplay();
        show("modify");
    }
}

function getChoice()
{
    // find selected RADIO, RETURN selected value
    var num;
    for(var i = 0; i < document.choices.radio.length; i++)
    {
        if(document.choices.radio[i].checked == true)
            num = parseInt(document.getElementById("s"+i).textContent);
    }
    return num;
}

function swap()
{
    editing = true;

    // swap text with fields
    for(var i = 0; i < document.choices.radio.length; i++)
    {
        var span = document.getElementById("s"+i);
        var num = parseInt(span.textContent);

        previousValues[i] = num;

        var html = "<input class='input-mini' type='text' name='custom' id='c"+i;
        html += "' value='"+num;
        html += "'>";
        // used to select on click and auto save on change

        span.innerHTML = html;
    }

    // swap edit button with done button
    var butt = document.getElementById("swapper");
    butt.innerHTML = "<a href='#' id='done' class='btn'><i class='icon-ok'></i></a>";
    document.querySelector('#done').addEventListener('click', swapBack);
}

function swapBack()
{
    // swap fields with text
    for(var i = 0; i < document.choices.radio.length; i++)
    {
        var span = document.getElementById("s"+i);
        var num = parseInt(document.getElementById("c"+i).value);

        if(isValid(num))
        {
            localStorage[i] = num;
            span.textContent = num;
        }
        else
            span.textContent = previousValues[i];
    }

    // swap done button with edit button
    var butt = document.getElementById("swapper");
    butt.innerHTML = "<a href='#' id='wrench' class='btn'><i class='icon-wrench'></i></a>";
    document.querySelector('#wrench').addEventListener('click', swap);

    editing = false;
}

function setTimer()
{
    // make sure we're dealing with text not fields
    if(editing)
        swapBack();

    // SET background timer for selected number
    // HIDE settings, DISPLAY countdown

    var num = getChoice();

    // set timer, hide settings, display reset button
    if(isValid(num))
    {
        bgpage.accountabilityPartner = document.querySelector("#friend-list").value;
        bgpage.accountabilityMoney = document.querySelector("#betAmount").value;
        bgpage.startTime = + new Date();
        bgpage.setAlarm(num * 60000);
        hide("settings");
        show("modify");
        show("display");
        document.querySelector("#moneyOnLine").innerText = bgpage.accountabilityMoney;
        refreshDisplay();
    }
    else
        bgpage.error();
}

// Returns true if 0 <= amt <= 240
function isValid(amt)
{
    if(isNaN(amt) || (amt == null))
        return false;
    else if((amt < 0) || (amt > 240))
        return false;
    else
        return true;
}

function refreshDisplay()
{
    percent = bgpage.getTimeLeftPercent();

    if(percent < 15)
        document.getElementById("bar").style.color = "grey";
    document.getElementById("bar").textContent = bgpage.getTimeLeftString();
    document.getElementById("bar").style.width = percent + "%";

    if (percent < 0.5) {
        hide("cancel");
        show("sucessAlert");
    }

    refreshDisplayTimeout = setTimeout(refreshDisplay, 100);
}

function pauseTimer()
{
    hide("pause");
    showInline("resume");
    bgpage.pause();
    clearTimeout(refreshDisplayTimeout);
}

function resumeTimer()
{
    hide("resume");
    showInline("pause");
    refreshDisplay();
    bgpage.resume();
}

function restartTimer()
{
    hide("resume");
    showInline("pause");
    refreshDisplay();
    bgpage.restart();
}

function reset()
{
    if (isVisible("sureCancel")) {
        clearTimeout(refreshDisplayTimeout);
        bgpage.turnOff();
        hide("display");
        show("settings");
        hide("modify");
        chrome.storage.local.get(['accessToken'], function(result) {
            sendFailureCall(result.accessToken);
        });
    }
    else {
        show("sureCancel");
    }
}

function login()
{
    var username = document.querySelector('#exampleInputEmail1').value;
    var password = document.querySelector('#exampleInputPassword1').value;
    console.log("User attempted to login in, username = " + username + " password = " + password);
    let data = {username: username, password: password};
    console.log(data);

    (async () => {
        const rawResponse = await fetch('https://ccd8-2a00-79e1-abc-c11-e86b-e81e-76cf-cef3.ngrok.io/api/login/', {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(data)
        });
        const content = await rawResponse.json();

        const responseStatus = rawResponse.status;

        console.log(responseStatus);
      
        console.log(content);

        chrome.storage.local.set({"refreshToken" : content.refresh}, function() {
            console.log("Refresh token set.");
        });

        chrome.storage.local.set({"accessToken" : content.access}, function() {
            console.log("Access token set.");
        });

        chrome.storage.local.set({'isLoggedIn' : "yes"}, function() {
            console.log("Logged in!");
        })

        if (responseStatus == 200) {
            bgpage.isLoggedIn = true;
            hide("login");
            show("settings");
        }
        else {
            show("wrongPassword");
        }

        
      })();
}

function logout() {
    chrome.storage.local.set({"refreshToken" : ""}, function() {
        console.log("Refresh token de-set.");
    });

    chrome.storage.local.set({"accessToken" : ""}, function() {
        console.log("Access token de-set.");
    });

    chrome.storage.local.set({'isLoggedIn' : "no"}, function() {
        console.log("Logged out!");
    })
    bgpage.isLoggedIn = false;
    hide("settings");
    show("login");
}

function sendFailureCall(accessToken) {
    console.log(bgpage.startTime);
    console.log(+ new Date());
    let data = {'accountable_dude' : bgpage.accountabilityPartner, 'start_time' : bgpage.startTime/1000, 'end_time' : (+ new Date())/1000, 'money' : bgpage.accountabilityMoney, 'success' : false};
    (async () => {
        const rawResponse = await fetch('https://ccd8-2a00-79e1-abc-c11-e86b-e81e-76cf-cef3.ngrok.io/authed/flow/new_flow/', {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' +  accessToken

          },
          body: JSON.stringify(data)
        });
        const content = await rawResponse.json();

        const responseStatus = rawResponse.status;

        console.log(responseStatus);
      
        console.log(content);
    })();
}
