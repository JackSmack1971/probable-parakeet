(function() {
  // Get the navigation menu and its list items
  const menu = document.querySelector('nav .nav-menu ul');

  // Add an event listener to the navigation menu using event delegation
  menu.addEventListener('click', function(e) {
    const target = e.target;

    // Check if the clicked element is an anchor inside the menu
    if (target.tagName === 'A' && target.closest('nav ul')) {
      e.preventDefault();

      const section = document.querySelector(target.getAttribute('href'));

      section.scrollIntoView({
        behavior: 'smooth'
      });
    }
  });

  // Get the "Shop Now" button and add an event listener to it
  const shopNowBtn = document.querySelector('.btn');
  shopNowBtn.addEventListener('click', function(e) {
    // Prevent the default behavior of the button
    e.preventDefault();

    // Alert the user that the shop is not yet available
    alert('The shop is not yet available.');
  });
})();
