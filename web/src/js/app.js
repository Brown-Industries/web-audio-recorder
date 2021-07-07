//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;

var gumStream; 						//stream from getUserMedia()
var rec; 							//Recorder.js object
var input; 							//MediaStreamAudioSourceNode we'll be recording

// shim for AudioContext when it's not avb. 
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext //audio context to help us record

var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");
var statusButton = document.getElementById("statusButton");

var duration = document.getElementById("duration");

var serverStatus = {HTTPStatus:null, isRecording:false, timeStarted:null};

//add events to those 2 buttons
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);
statusButton.addEventListener("click", getStatus);


var intervalId = window.setInterval(function(){
	getStatus()
  }, 1000);

function startRecording() {
	console.log("recordButton clicked");
	queryServer("startRecording");
	stopButton.disabled = false;
	recordButton.disabled = true;
}
var jsonResponse;
function queryServer(endpoint) {
	const Http = new XMLHttpRequest();
	Http.responseType = 'json';
	const path = endpoint;
	const url = "/api/";
	Http.open("GET", url + path);
	console.log(url+path);
	Http.send();

	Http.onreadystatechange = (e) => {
		jsonResponse = Http.response;
		serverStatus.HTTPStatus = Http.response.HTTPStatus;
		serverStatus.isRecording = Http.response.isRecording;
		serverStatus.timeStarted = Http.response.timeStarted;
	}
}

function getStatus(){
	queryServer("status");

	if(serverStatus.isRecording){
		stopButton.disabled = false;
		recordButton.disabled = true;

		var startTime = new Date(0); // The 0 there is the key, which sets the date to the epoch
		startTime.setUTCSeconds(serverStatus.timeStarted);

		var timePassed = Date.now() - startTime;
		
		duration.innerText = Math.floor(timePassed/1000) + " seconds";
	}else{
	duration.innerText = "";
	}
}

function stopRecording() {
	console.log("stopButton clicked");

	//disable the stop button, enable the record too allow for new recordings
	stopButton.disabled = true;
	recordButton.disabled = false;

	queryServer("stopRecording");
	
	//create the wav blob and pass it on to createDownloadLink
	//rec.exportWAV(createDownloadLink);
}

function createDownloadLink(blob) {
	
	var url = URL.createObjectURL(blob);
	var au = document.createElement('audio');
	var li = document.createElement('li');
	var link = document.createElement('a');

	//name of .wav file to use during upload and download (without extendion)
	var filename = new Date().toISOString();

	//add controls to the <audio> element
	au.controls = true;
	au.src = url;

	//save to disk link
	link.href = url;
	link.download = filename+".wav"; //download forces the browser to donwload the file using the  filename
	link.innerHTML = "Save to disk";

	//add the new audio element to li
	li.appendChild(au);
	
	//add the filename to the li
	li.appendChild(document.createTextNode(filename+".wav "))

	//add the save to disk link to li
	li.appendChild(link);
	
	//upload link
	var upload = document.createElement('a');
	upload.href="#";
	upload.innerHTML = "Upload";
	upload.addEventListener("click", function(event){
		  var xhr=new XMLHttpRequest();
		  xhr.onload=function(e) {
		      if(this.readyState === 4) {
		          console.log("Server returned: ",e.target.responseText);
		      }
		  };
		  var fd=new FormData();
		  fd.append("audio_data",blob, filename);
		  xhr.open("POST","upload.php",true);
		  xhr.send(fd);
	})
	li.appendChild(document.createTextNode (" "))//add a space in between
	li.appendChild(upload)//add the upload link to li

	//add the li element to the ol
	recordingsList.appendChild(li);
}