document.addEventListener('DOMContentLoaded', function() {

    // like and unlike listener
    document.querySelectorAll('.fa-heart').forEach(div => {
        div.onclick = function() {
            likeDislike(this);
        }
    })

    // Edit button listener
    document.querySelectorAll('#edit-btn').forEach(button => {
        button.onclick = function() {
            edit(this);
        }
    })

    // follow and unfollow listener
    document.querySelector('#follow').addEventListener('click', function() {
        fetch(`/follow/${this.dataset.id}`)
            .then(response => response.json())
            .then(res => {
                document.querySelector('#followers').innerHTML = `Followers: ${res.followers}`

                if(res.result === 'Follow') {
                    this.innerHTML = 'Unfollow'
                    this.className = 'btn btn-sm btn-outline-secondary'
                } else {
                    this.innerHTML = 'Follow'
                    this.className = 'btn btn-sm btn-outline-primary'
                }
            });
    });
})

// For liking and un-liking posts
async function likeDislike(element) {
    await fetch(`/like/${element.dataset.id}`)
    .then(response => response.json())
    .then(res => {
        element.className = res.css_class;
        element.querySelector('small').innerHTML = res.likes;
    });
}

// For editing posts
async function edit(button) {

    let body = document.querySelector(`#post${button.dataset.id}`)

    let form = body.querySelector('form')
    let old_text = body.querySelector('#text');

    old_text.style.display = 'none';
    button.style.display = 'none';

    let new_text = body.querySelector('textarea');
    new_text.innerHTML = old_text.innerHTML;

    let save_btn = body.querySelector('button');
    
    form.style.display = 'block';

    form.onsubmit = () => {
        fetch('edit', {
            method: 'POST',
            body: JSON.stringify({
                new_text: new_text.value,
                id: button.dataset.id
            })
        })
            .then(response => response.json())
                .then(res => {
                    console.log(res);

                    form.style.display = 'none';
                    body.querySelector('#text').innerHTML = res.text;
                    old_text.style.display = 'block';
                    button.style.display = 'block';
                })
                .catch(error => {
                    console.log(error);
                });

        return false;
    };
}