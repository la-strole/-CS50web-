import { editPostApi } from './api.js'

function editButtonClick () {
  // Show postEdit form
  // Find Post from Editbutton data
  const post = document.querySelector(`#${this.dataset.postid}`)
  // Show post Edit form
  const postEditForm = post.querySelector('.posteditform')
  postEditForm.style.display = 'block'
  // Hide edit button
  this.style.display = 'none'
  // Hide old text
  const oldText = post.querySelector('.card-text')
  oldText.style.display = 'none'
}

function saveButtonClick (saveButton) {
  // Get Post info to send to server
  const post = document.querySelector(`#${saveButton.dataset.postid}`)
  const postText = post.querySelector('.posttext').value
  const postId = saveButton.dataset.postid.slice(2)
  // Send to server
  const result = editPostApi(postId, postText)
  // Than get approved status
  result.then((data) => {
    // Hide edit post form
    const postEditForm = post.querySelector('.posteditform')
    postEditForm.style.display = 'none'
    // Show edit button
    const editButton = post.querySelector('.editbutton')
    editButton.style.display = 'inline'
    // Show regular post text card
    const oldText = post.querySelector('.card-text')
    oldText.style.display = 'block'
    if (data.status === 'success') {
      // Put text to regular post card
      oldText.innerHTML = postText
    } else {
      // Return to old post
      // Restore old text
      console.error('Error with edit post API')
    }
  })
}

document.addEventListener('DOMContentLoaded', () => {
  // Find Edit buttons and add Eventlisteners to them
  const editButtons = document.querySelectorAll('.editbutton')
  editButtons.forEach((editButton) => { editButton.addEventListener('click', editButtonClick) })
  // Find Save buttons and add Eventlisteners to them
  const saveButtons = document.querySelectorAll('.savebutton')
  saveButtons.forEach((saveButton) => {
    saveButton.addEventListener('click', (event) => {
    // Prevent deafilt Form behaviour
      event.preventDefault()
      saveButtonClick(saveButton)
    })
  })
})
