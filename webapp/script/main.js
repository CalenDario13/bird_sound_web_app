API_ENDPOINT = "https://uo8jn9b563.execute-api.us-east-1.amazonaws.com/default"


document.getElementById('inp').onchange = function(event) {
    var mybird = Audio()
    var myaudio = document.getElementById('player');
    myaudio.src = URL.createObjectURL(event.target.files[0]); 
  };
  
document.getElementById('play').onclick = function(){
    document.getElementById('player').play();
};


document.getElementById('player').ontimeupdate = function() {
    var bar = document.getElementById('seekbar');
    var sound = document.getElementById('player');
    var dur = sound.duration;
    bar.value = sound.currentTime / dur;
};

 
document.getElementById("genre").onclick = function(){
    var sound = document.getElementById("player")
    var mysound = sound.toDataURL()
	  var inputData = {"data": mysound};
 
    $.ajax({
      url: API_ENDPOINT,
      type: 'POST',
      crossDomain: true,
      data: JSON.stringify(inputData),
      dataType: 'json',
      contentType: "application/json",
      success: function (response) {
        document.getElementById("genreReturned").textContent = response;
      },
  });
}