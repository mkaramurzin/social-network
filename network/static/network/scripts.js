document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.fa-heart').forEach(div => {
        div.onclick = function() {
            likeDislike(this);
        }
    })
})

// For liking and un-liking posts
async function likeDislike(element) {
    await fetch(`/like/${element.dataset.id}`)
        .then(response => response.json())
        .then(data => {
            element.className = data.css_class;
            element.querySelector('small').innerHTML = data.likes;
        });
}