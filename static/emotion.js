let RunEmotionDetector = ()=>{
    inputText = document.getElementById("inputText").value;

    let xhttpRequest = new XMLHttpRequest();
    xhttpRequest.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("sys_response").innerHTML = xhttpRequest.responseText;
        }
    };
    xhttpRequest.open("GET", "emotionDetector?inputText"+"="+inputText, true);
    xhttpRequest.send();
}
