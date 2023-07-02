const navBar = document.querySelector('nav')
const navatar = document.querySelector('.navatar')
const userMenu = document.querySelector('.userMenu')
const navDropdown = userMenu.querySelector('.navDropdown')
const postMenu = document.querySelector('.postMenu')
const postDropdown = postMenu.querySelector('.postDropdown')
const userTabs = document.querySelector('.profileTabs')

document.addEventListener("scroll", (event) => {
    let navBarTop = navBar.getBoundingClientRect().top
    if (navatar.classList.contains('top') && navBarTop > 0) {
        navatar.classList.remove('top')
        navBar.classList.remove('navTop')
    } else {
        if (navBarTop < 0) {
            navatar.classList.add('top')
            navBar.classList.add('navTop')
        }
    }
})

userMenu.addEventListener("mouseover", (event) => {
    userMenu.querySelector('.arrow').classList.add('rotate180')
    navDropdown.classList.remove('hide')    
})
userMenu.addEventListener("mouseout", (event) => {
    userMenu.querySelector('.arrow').classList.remove('rotate180')
    navDropdown.classList.add('hide')
})

postMenu.addEventListener("mouseover", (event) => {
    postDropdown.classList.remove('hide')    
})
postMenu.addEventListener("mouseout", (event) => {
    postDropdown.classList.add('hide')
})

const likedClass = 'fa-solid fa-heart'
const unlikedClass = 'fa-regular fa-heart'

function like(userID, postID) {
    const likeIcon = document.querySelector('.like').querySelector('i')
    fetch('/like/' + postID, {
        method: 'PUT',
        body: JSON.stringify({
            user: userID
        })
    })
    likeIcon.classList = likedClass
    likeIcon.onclick = () => {
        unlike(userID, postID)
    }
}

function unlike(userID, postID) {
    const likeIcon = document.querySelector('.like').querySelector('i')
    fetch('/unlike/' + postID, {
        method: 'PUT',
        body: JSON.stringify({
            user: userID
        })
    }) 
    likeIcon.classList = unlikedClass
    likeIcon.onclick = () => {
        like(userID, postID)
    }
}

function follow(sourceID, targetName) {
    fetch('/follow/' + targetName, {
        method: 'PUT',
        body: JSON.stringify({
            source: sourceID
        })
    })
    document.querySelector('.followUser').classList = '.unfollowUser'
}

function unfollow(sourceID, targetName) {
    fetch('/unfollow/' + targetName, {
        method: 'PUT',
        body: JSON.stringify({
            source: sourceID
        })
    })
    document.querySelector('.unfollowUser').classList = '.followUser'
}

if (userTabs) {
    const tabs = userTabs.querySelectorAll('a')
    let currPage = window.location.href.split('/').pop()
    let tabFound = false
    for (let tab of tabs) {
        let tabText = tab.innerText.toLowerCase()
        if (tabText == currPage) {
            tab.classList.add('active')
            tabFound = true
        }
    }
    if (!tabFound) {
        tabs[0].classList.add('active')
    }
}