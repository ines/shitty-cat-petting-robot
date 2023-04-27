const statusEl = document.querySelector('.status')
const handEl = document.querySelector('.hand')
const handRect = handEl.getBoundingClientRect()
const statusActiveClass = 'status-active'
const handActiveClass = 'hand-active'

let moved = null
let start = null


window.addEventListener('DOMContentLoaded', () => {
    fetch('/health').then(res => {
        if (res.status == 200) {
            statusEl.classList.add(statusActiveClass)
        }
    })
})

window.addEventListener('mousedown', event => {
    moved = null
    start = event.clientX
    handEl.classList.add(handActiveClass)
})

window.addEventListener('mousemove', event => {
    moved = true
    handEl.style.top = event.clientY - handRect.height / 2
    handEl.style.left = event.clientX - handRect.width / 2
})

window.addEventListener('mouseup', event => {
    if (moved != null) {
        handEl.classList.remove(handActiveClass)
        const end = event.clientX
        if (start != end) {
            const trueStart = start < end ? start : end
            const trueEnd = start < end ? end : start
            const width = document.body.clientWidth
            const data = {
                start: trueStart / width,
                end: trueEnd / width,
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
