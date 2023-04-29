const statusEl = document.querySelector('.status')
const handEl = document.querySelector('.hand')
const handRect = handEl.getBoundingClientRect()

let moved = null
let start = null


window.addEventListener('DOMContentLoaded', () => {
    fetch('/health').then(res => {
        if (res.ok) {
            statusEl.classList.add('status-active')
        }
    })
})

window.addEventListener('mousedown', event => {
    moved = null
    start = event.clientX
    handEl.classList.add('hand-active')
})

window.addEventListener('mousemove', event => {
    moved = true
    handEl.style.top = event.clientY - handRect.height / 2
    handEl.style.left = event.clientX - handRect.width / 2
})

window.addEventListener('mouseup', event => {
    if (moved != null) {
        handEl.classList.remove('hand-active')
        const end = event.clientX
        if (start != end) {
            const width = document.body.clientWidth
            const data = {
                start: (start < end ? start : end) / width,
                end: (start < end ? end : start) / width,
            }
            fetch('/pet', {
                method: 'POST', body: JSON.stringify(data), headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            })
        }
    }
})
