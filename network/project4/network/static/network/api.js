// Following relationship
export async function followwingRel (fallowTo, fallowFrom) {
  try {
    const csrfToken = Cookies.get('csrftoken')
    const url = '/api/follow'
    const response = await fetch(url, {
      method: 'PUT',
      headers: {
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({
        fallowTo,
        fallowFrom
      })
    }
    )
    if (!response.ok) {
      throw new Error('Network response was not OK')
    }

    const data = response.json()
    return data
  } catch (error) {
    console.error('There has been a problem with followwing relations:', error)
  }
}

export async function editPostApi (postId, postText) {
  try {
    const csrfToken = Cookies.get('csrftoken')
    const url = '/api/editpost'
    const response = await fetch(url, {
      method: 'PUT',
      headers: {
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({
        postId,
        postText
      })
    }
    )
    if (!response.ok) {
      throw new Error('Network response was not OK')
    }

    const data = response.json()
    return data
  } catch (error) {
    console.error('There has been a problem with followwing relations:', error)
  }
}
