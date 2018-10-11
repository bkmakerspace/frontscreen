showTime = ->
    date = new Date()
    h = date.getHours()
    m = date.getMinutes()
    s = date.getSeconds()
    session = "AM"
    if h == 0
        h = 12
    if h > 12
        h = h - 12
        session = "PM"
    h = if h < 10 then "0" + h else h
    m = if m < 10 then "0" + m else m
    s = if s < 10 then "0" + s else s
    time = h + ":" + m + ":" + s + " " + session
    document.getElementById("clock").innerText = time
    document.getElementById("clock").textContent = time
    setTimeout showTime, 1000
showTime()
