
var getCaptureThermal = function(theUrl) {
    var xhr = new XMLHttpRequest()
    console.log(`Start GET: ${theUrl}`)
    document.getElementById('thermal_image').style.display = 'none'
    document.getElementById('img_placeholder').style.display = 'inline-block'
    document.getElementById('img_placeholder_text').innerHTML  = 'Processing'
    xhr.open("GET", theUrl, true)
    xhr.onreadystatechange = function (e) {
        if(this.readyState == 4 && this.status === 200) {
            console.log(xhr.response)
            responseJSON = JSON.parse(xhr.response)
            getThermalUrl = '/get_thermal/' + responseJSON.frame_num
            document.getElementById('thermal_image').src=getThermalUrl
            document.getElementById('thermal_image').style.display = 'inline-block'
            document.getElementById('img_placeholder').style.display = 'none'
            document.getElementById('temperatureText').innerHTML = responseJSON.temp
            console.log("set image path" + getThermalUrl)
            //resultBox.innerHTML = "Wrote to : " + responseJSON.fileList.join('; ')
        }
    }
    xhr.send()
}

