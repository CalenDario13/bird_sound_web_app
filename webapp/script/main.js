API_ENDPOINT = "https://fn5zu5vj91.execute-api.us-east-1.amazonaws.com/bird-web-app"


function showMenu() {
        document.getElementById("mySidebar").style.width = "250px";
        document.getElementById("main").style.marginLeft = "250px";
}

document.getElementById("inp"){


}




let audio = document.getElementById("inp").files[0];
let formData = new FormData();
formData.append("audio", audio);
$.ajax({
        url: API_ENDPOINT,
        type: 'POST',
        crossDomain: true,
        data: JSON.stringify(formData),
        dataType: 'json',
        contentType: "application/json",
        success: function (response) {
        document.getElementById("genreReturned").textContent = response;
        },
});
