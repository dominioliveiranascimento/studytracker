let seconds = 0
let interval = null



function formatTime(totalSeconds) {


    let hours = Math.floor(totalSeconds / 3600)

    let minutes = Math.floor((totalSeconds % 3600) / 60)

    let secs = totalSeconds % 60

    hours = String(hours).padStart(2, "0")
    minutes = String(minutes).padStart(2, "0")
    secs = String(seconds).padStart(2, "0")

    return `${hours}:${minutes}:${secs}`
}



document.getElementById("start").onclick = function () {

    if (interval === null) {

        seconds = 0 

        document.getElementById("msg").innerText = ""

        interval = setInterval(() => {
        seconds++

        document.getElementById("timer").innerText = formatTime(seconds)

       }, 1000)

    }

}


document.getElementById("stop").onclick = function () {

    clearInterval(interval)
    interval = null

    if (seconds > 0) {

        let finalTime = formatTime(seconds)

        document.getElementById("msg").innerText = 
        "Parabéns! Seu tempo de estudo foi de " + finalTime

        let minutos = Math.floor(seconds / 60)

        fetch("/save-timer", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                tempo: minutos
            })
        })
    }

}