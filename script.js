function analyzeComments() {
    var youtubeLink = document.getElementById("youtubeLink").value;
    
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/analyze", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            var positivePercentage = response.positive;
            var neutralPercentage = response.neutral;
            var negativePercentage = response.negative;

            document.getElementById("positive").innerText = positivePercentage + "% Positive";
            document.getElementById("neutral").innerText = neutralPercentage + "% Neutral";
            document.getElementById("negative").innerText = negativePercentage + "% Negative";
        }
    };
    var data = JSON.stringify({ "youtubeLink": youtubeLink });
    xhr.send(data);
}


