// script.js 

function renderGallery(galleryData, filter = '', sortBy = '') {
  const gallerySection = document.querySelector('.gallery');
  gallerySection.innerHTML = ''; 

  const filteredData = galleryData.filter((artwork) => {
    if (filter) {
      return artwork.category.toLowerCase() === filter.toLowerCase();
    }
    return true;
  }); 

  const sortedData = filteredData.sort((a, b) => {
    if (sortBy === 'title') {
      return a.title.localeCompare(b.title);
    }
    return 0;
  }); 

  sortedData.forEach((artwork) => {
    const artworkElement = document.createElement('article');
    artworkElement.innerHTML = `
      <figure>
        <img src="${artwork.image}" alt="${artwork.title}" loading="lazy">
        <figcaption>
          <h2>${artwork.title}</h2>
          <p>${artwork.description}</p>
        </figcaption>
      </figure>
    `;
    gallerySection.appendChild(artworkElement);
  });
} 

function debounce(func, wait) {
  let timeout;
  return function () {
    const context = this;
    const args = arguments;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), wait);
  };
} 

async function fetchGalleryContent() {
  const gallerySection = document.querySelector('.gallery'); 

  try {
    const response = await fetch('path/to/your/data.json');
    const galleryData = await response.json(); 

    const debouncedRenderGallery = debounce(renderGallery, 300);
    document.querySelector('#filterControl').addEventListener('change', (e) => {
      const filterValue = e.target.value;
      debouncedRenderGallery(galleryData, filterValue);
    }); 

    document.querySelector('.gallery-controls input[type="search"]').addEventListener(
      'input',
      debounce((e) => {
        searchArtworks(e.target.value, galleryData);
      }, 300)
    ); 

    // Render the gallery content
    renderGallery(galleryData);
  } catch (error) {
    console.error('Error fetching gallery data:', error);
    gallerySection.innerHTML = '<p>Error loading gallery content. Please try again later.</p>';
  }
} 

function paginateGallery(pageNumber, itemsPerPage, galleryData) {
  const startIndex = (pageNumber - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const slicedData = galleryData.slice(startIndex, endIndex);
  renderGallery(slicedData);
} 

function openLightbox(src) {
  if (!src) {
    console.error('No image source provided for the lightbox');
    return;
  } 

  const lightbox = document.createElement('div');
  lightbox.classList.add('lightbox');
  const img = document.createElement('img');
  img.setAttribute('src', src);
  lightbox.appendChild(img);
  document.body.appendChild(lightbox); 

  img.setAttribute('aria-labelledby', 'lightboxLabel');
  lightbox.setAttribute('role', 'dialog');
  lightbox.setAttribute('aria-labelledby', 'lightboxLabel'); 

  const label = document.createElement('span');
  label.id = 'lightboxLabel';
  label.innerText = 'Image lightbox';
  label.style.position = 'absolute';
  label.style.left = '-9999px';
  label.style.top = '-9999px';
  lightbox.appendChild(label); 

  lightbox.addEventListener('click', () => {
    lightbox.remove();
  }); 

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      lightbox.remove();
    }
  });
} 

function searchArtworks(query, galleryData) { 

const filteredData = galleryData.filter((artwork) => { const regex = new RegExp(query, 'gi'); return artwork.title.match(regex) || artwork.description.match(regex); }); renderGallery(filteredData); } 

document.addEventListener('DOMContentLoaded', function () { fetchGalleryContent(); }); 

document.querySelectorAll('.gallery article').forEach((article) => { article.addEventListener('click', () => { const imgSrc = article.querySelector('img').getAttribute('src'); openLightbox(imgSrc); }); });
