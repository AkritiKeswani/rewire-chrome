// chrome.storage.local.set({"isBlockingEnabled" : true});

blocklist = []

chrome.storage.local.get(['blocklist'], function(result) {
    blocklist = result.blocklist;
});

chrome.storage.local.get(['isBlockingEnabled'], function(result) {
    domain = window.location.hostname;
    // handle www
    if (window.location.hostname.includes("www.")) {
        domain = window.location.hostname.substring(4);
    }
    if (result.isBlockingEnabled && blocklist.includes(domain)) {
        document.getElementsByTagName("html")[0].innerHTML = "<html><head><title>Focus on work!</title><style>body{background: #A8D8E3;font-family: 'Enriqueta', arial, serif;}.container{position: fixed;top: 0px;left: 0px;width: 100%;height: 100%;z-index: 0;background: -webkit-radial-gradient(rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.3) 35%, rgba(0, 0, 0, 0.7));background: -moz-radial-gradient(rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.3) 35%, rgba(0, 0, 0, 0.7));background: -ms-radial-gradient(rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.3) 35%, rgba(0, 0, 0, 0.7));background: radial-gradient(rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.3) 35%, rgba(0, 0, 0, 0.7));}.content{position: absolute;width: 100%;height: 100%;left: 0px;top: 0px;z-index: 1000;}.container h2{position: absolute;top: 50%;line-height: 100px;height: 100px;margin-top: -50px;font-size: 80px;width: 100%;text-align: center;color: transparent;animation: blurFadeInOut 3s ease-in backwards;}.container h2.frame-1{animation-delay: 0s;}.container h2.frame-2{animation-delay: 2.5s;}.container h2.frame-3{animation-delay: 5s;}.container h2.frame-4{font-size: 120px;animation-delay: 7.5s;}.container h2.frame-5{animation: none;color: transparent;text-shadow: 0px 0px 1px #fff;}.container h2.frame-5 span{animation: blurFadeIn 4s ease-in 12s backwards;color: transparent;text-shadow: 0px 0px 1px #fff;}.container h2.frame-5 span:nth-child(2){animation-delay: 13s;}.container h2.frame-5 span:nth-child(3){animation-delay: 14s;}@keyframes blurFadeInOut{0%{opacity: 0;text-shadow: 0px 0px 40px #fff;transform: scale(0.9);}20%,75%{opacity: 1;text-shadow: 0px 0px 1px #fff;transform: scale(1);}100%{opacity: 0;text-shadow: 0px 0px 50px #fff;transform: scale(0);}}@keyframes blurFadeIn{0%{opacity: 0;text-shadow: 0px 0px 40px #fff;transform: scale(1.3);}50%{opacity: 0.5;text-shadow: 0px 0px 10px #fff;transform: scale(1.1);}100%{opacity: 1;text-shadow: 0px 0px 1px #fff;transform: scale(1);}}@keyframes fadeInBack{0%{opacity: 0;transform: scale(0);}50%{opacity: 0.2;transform: scale(2);}100%{opacity: 0.1;transform: scale(5);}}</style></head><body><div class='container'><div class='content'><h2 class='frame-1'>Unforunately...</h2><h2 class='frame-2'>You are experiencing some context switching!</h2><h2 class='frame-3'>Research shows it may take 50% longer to complete your task than originally planned. </h2><h2 class='frame-4'>Let's get back to it!</h2><h2 class='frame-5'><span>What are you waiting for?</span> <span>Save your brain power!</span> </h2></div></body></html>";
    }
  });