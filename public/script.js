function httpGet(theUrl) {
    
    var username = document.getElementById("username").value
    var xhr = new XMLHttpRequest()
    var urlWithParams = theUrl + "/" + username
    console.log(urlWithParams)
    xhr.open("GET", urlWithParams, true)
    xhr.onreadystatechange = function (e) {
        if(this.readyState == 4 && this.status === 200) {
            console.log(xhr.response)
            responseJSON = JSON.parse(xhr.response)
            var resultBox = document.getElementById("resultBox")
            console.log(resultBox)
            resultBox.innerHTML = "Wrote to : " + responseJSON.fileList.join('; ')
        }
    }
    xhr.send()
}
