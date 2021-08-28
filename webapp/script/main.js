const API_ENDPOINT = "https://mt8ao5cle9.execute-api.us-east-1.amazonaws.com/statusoQuo";

function saveAudio(event) {
  const audio = event.target.files[0];
  const audioContainer = document.querySelector('#myAudio'); 
  audioContainer.src = URL.createObjectURL(audio); 
  return audio
};

async function audioToBase64(audioFile) {
  return new Promise((resolve, reject) => {
    let reader = new FileReader();
    reader.onerror = reject;
    reader.onload = (e) => resolve(e.target.result);
    reader.readAsDataURL(audioFile);
  });
};

async function processAudio(event){
  // Save Original Audio
  const audioFile = saveAudio(event);
  // Convert TO Base64
  const Base64Audio = await audioToBase64(audioFile)
  // Save Base64 into the web App
  let a = document.createElement("a"); 
  a.href = Base64Audio;
  a.className = 'linkToFile'
  document.body.appendChild(a); 
  console.log("File Succesfully Loaded")
};

// Behaviour of clicking on load Button
document.querySelector('#loadButton').addEventListener('change', processAudio )

// Behaviour of clicking on Play Button
document.querySelector('#play').addEventListener('click', function() {
    document.querySelector('#myAudio').play();
  });

// Behaviour of the SeekBar
document.querySelector('#myAudio').addEventListener('timeupdate', function() {
    const bar = document.querySelector('#seekbar');
    const sound = document.querySelector('#myAudio');
    let dur = sound.duration;
    let value = sound.currentTime / dur;
});


// Behaviour of the button to Get the Response:
document.getElementById("lambdaConnect").onclick = function(){

  const container = document.querySelector('.linkToFile');
  const base64 = container.href;
  const inputData = {"data": base64};

  $.ajax({
    url: API_ENDPOINT,
    type: 'POST',
    crossDomain: true,
    data: JSON.stringify(inputData),
    dataType: 'json',
    contentType: "application/json",
    success: function (response) {
      document.getElementById("response").textContent = response;
    },
});
}
