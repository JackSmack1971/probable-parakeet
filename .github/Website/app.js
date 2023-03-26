// get the navigation menu and its list items
const menu = document.querySelector('nav ul');
const menuItems = menu.querySelectorAll('li a');

// add an event listener to each menu item
menuItems.forEach(item => {
  item.addEventListener('click', function(e) {
    // prevent the default behavior of the link
    e.preventDefault();

    // get the section that corresponds to the clicked menu item
    const section = document.querySelector(this.getAttribute('href'));

    // scroll to the section smoothly
    section.scrollIntoView({
      behavior: 'smooth'
    });
  });
});

// get the "Shop Now" button and add an event listener to it
const shopNowBtn = document.querySelector('.btn');
shopNowBtn.addEventListener('click', function(e) {
  // prevent the default behavior of the button
  e.preventDefault();

  // alert the user that the shop is not yet available
  alert('The shop is not yet available.');
});
