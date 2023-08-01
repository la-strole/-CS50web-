import { followwingRel } from './api.js'

document.addEventListener('DOMContentLoaded', () => {
  const followButton = document.querySelector('#followButton')
  const followersCount = document.querySelector('#followersCount')
  if (followButton) {
    followButton.addEventListener('click', () => {
      const result = followwingRel(followButton.dataset.followto, followButton.dataset.followfrom)
      result.then((data) => {
        if (data.status === 'success') {
          if (followButton.value === 'Follow') {
            followButton.textContent = 'Unfollow'
            followButton.value = 'Unfollow'
            followersCount.innerHTML = parseInt(followersCount.innerHTML) + 1
          } else {
            followButton.textContent = 'Follow'
            followButton.value = 'Follow'
            followersCount.innerHTML = parseInt(followersCount.innerHTML) - 1
          }
        }
      })
    })
  }
})
