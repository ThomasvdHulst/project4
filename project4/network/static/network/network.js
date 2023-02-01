//Function that waits a given amount of miniseconds, to ensure all calls to the database are done.
function wait(milliseconds) {
    const this_date = Date.now();
    let currentDate = null;
    do {
      currentDate = Date.now();
    } while (currentDate - this_date < milliseconds);
  }


document.addEventListener('DOMContentLoaded', function() {

    load_posts();

});

function load_posts() {
    user_id = parseInt(document.querySelector('.user_id').innerHTML);

    function manage_likes(like) {
        fetch(`/posts/${like.dataset.post_id}`)
        .then(response => response.json())
        .then(post => {
            if (post.liked_by.includes(user_id)) {
                like.innerHTML = '&#10084 ' + post.likes;
            } else {
                like.innerHTML = '&#129293; ' + post.likes;
            }

            like.onclick = () => {
                let new_liked_by = []
                let new_likes = 0

                if (post.liked_by.includes(user_id)) {
                    new_likes = post.likes - 1;
                    const index = post.liked_by.indexOf(user_id);
                    post.liked_by.splice(index, 1);

                    if (post.liked_by.length > 0) {
                        new_liked_by = post.liked_by.toString(",");
                    }

                    like.innerHTML = '&#129293; ' + new_likes;
                } else {
                    new_likes = post.likes + 1;

                    if (post.liked_by.length > 0) {
                        new_liked_by = post.liked_by.toString() + ',' + user_id;
                    } else {
                        new_liked_by = user_id;
                    }
                    
                    like.innerHTML = '&#10084; ' + new_likes;
                }

                fetch(`/posts/${post.id}`, {
                    method: 'PUT',
                    body: JSON.stringify({
                        likes: new_likes,
                        liked_by: String(new_liked_by)
                    })
                })

                //Wait 100 milli-seconds to ensure that the PUT request is done
                wait(100);
                load_posts();
            } 
        });  
    }

    function edit_post(edit) {
        fetch(`/posts/${edit.dataset.post_id}`)
        .then(response => response.json())
        .then(post => {
            //Extra check to see if the post is of the logged-in user
            if (post.user == user_id){
                document.querySelector(`#content-${post.id}`).style.display = 'none';

                document.querySelector(`#edit-post-content-${post.id}`).innerHTML = `<form id='edit-post'><textarea id='edit-post-area' class='form-control'>${post.content}</textarea>
                <br><input type='submit' class='btn btn-primary' value='Save' id='save-post'></form>`;

                document.querySelector(`#edit-post-content-${post.id}`).style.display = 'block';

                document.querySelector('#edit-post-area').onkeyup = () => {
                    if (document.querySelector('#edit-post-area').value.length > 2){
                        document.querySelector('#save-post').disabled = false;
                    } else {
                        document.querySelector('#save-post').disabled = true;
                    }  
                }

                document.querySelector('#edit-post').onsubmit = () => {
                    fetch(`/posts/${post.id}`, {
                        method: 'PUT',
                        body: JSON.stringify({
                            content: document.querySelector('#edit-post-area').value
                        })
                    })

                    document.querySelector(`#edit-post-content-${post.id}`).style.display = 'none';
                    document.querySelector(`#content-${post.id}`).innerHTML = document.querySelector('#edit-post-area').value;
                    document.querySelector(`#content-${post.id}`).style.display = 'block';
                    
                    return false
                }
            }
        }); 
    }

    document.querySelectorAll('.edit-post').forEach((edit) => {
        edit.onclick = () => {
            edit_post(edit);
        } 
    })

    document.querySelectorAll('.likes').forEach((like) => {
        manage_likes(like);
    })

    if (document.querySelector('#new-post-content')) {
        document.querySelector('#new-post-content').onkeyup = () => {
            if (document.querySelector('#new-post-content').value.length > 3){
                document.querySelector('#submit').disabled = false;
            } else {
                document.querySelector('#submit').disabled = true;
            }  
        }
    }

    if (document.querySelector('#follow-btn')) {
        const profile_id = parseInt(document.querySelector('#follow-btn').dataset.profile_id);

        fetch(`/following/${user_id}`)
        .then(response => response.json())
        .then(result => {
            if (result.following.includes(profile_id)) {
                document.querySelector('#follow-btn').innerHTML = 'Unfollow';
            } else {
                document.querySelector('#follow-btn').innerHTML = 'Follow';
            }

            document.querySelector('#follow-btn').onclick = () => {
                let new_following = '';
                const current_followers = parseInt(document.querySelector('#followers').innerHTML);

                if (result.following.includes(profile_id)) {
                    document.querySelector('#follow-btn').innerHTML = 'Follow';
                    document.querySelector('#followers').innerHTML = current_followers - 1;

                    const index = result.following.indexOf(profile_id);
                    result.following.splice(index, 1);

                    if (result.following.length > 0) {
                        new_following = result.following.toString(",");
                    } 
                } else {
                    document.querySelector('#follow-btn').innerHTML = 'Unfollow';
                    document.querySelector('#followers').innerHTML = current_followers + 1;

                    if (result.following.length > 0) {
                        new_following = result.following.toString() + ',' + profile_id;
                    } else {
                        new_following = profile_id;
                    }
                }

                fetch(`/following/${user_id}`, {
                    method: 'PUT',
                    body: JSON.stringify({
                        following: String(new_following)
                    })
                })

                //Wait 100 milli-seconds to ensure that the PUT request is done
                wait(100)
                load_posts();
            }
        });  
        
    }
}
