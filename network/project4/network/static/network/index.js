document.addEventListener('DOMContentLoaded', () => {
  const csrftoken = Cookies.get('csrftoken')
  // Render Posts in index view
  // Add 10 latest posts
  const postSection = document.querySelector('#postSection')
  getLatestPosts().then((posts) => {
    addListPostsToDom(posts, postSection)
  })

 

async function getLatestPosts () {
  const url = '/api/postsList'
  const response = await fetch(url)
  if (response.ok) {
    const posts = response.json()
    return posts
  } else {
    console.error(`Can not get latest posts. ststus: ${response.status}`)
  }
}

function addListPostsToDom (
  posts, // posts - return value of promise from getLatestPosts
  parrentElement // element to append ten posts to
) {
  for (let post of posts.response) {
    post = JSON.parse(post)
    const postElement = document.createElement('div')
    postElement.classList.add('card', 'mt-4')
    postElement.innerHTML = `
          <div class="card-body">
              <h5 class="card-title">${post.author}</h5>
              <a href="#" class="btn btn-primary">Edit</a>
              <p class="card-text">${post.postText}</p>
              <a href='#'>😻 ${post.likeCount}</a>
          </div>
          <div class="card-footer">${post.timestamp}</div>`
    parrentElement.appendChild(postElement)
  }
}
