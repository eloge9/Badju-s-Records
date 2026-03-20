// ─────────────────────────────────────────────
// FONCTIONS COMMUNES
// ─────────────────────────────────────────────

// ── Gestion des onglets ──
function showTab(tab) {
  document
    .querySelectorAll(".tab-content")
    .forEach(content => content.classList.remove("active"));
  
  document
    .querySelectorAll(".tab-btn")
    .forEach(btn => btn.classList.remove("active"));
  
  document.getElementById(tab).classList.add("active");
  event.target.classList.add("active");
}

// ── Gestion des fichiers (upload) ──
function handleFileSelect(input, type) {
  const file = input.files[0];
  const uploadDiv = input.parentElement;
  
  if (file) {
    uploadDiv.classList.add("has-file");
    const fileName = uploadDiv.querySelector(".file-name");
    if (fileName) {
      fileName.textContent = file.name;
    }
  } else {
    uploadDiv.classList.remove("has-file");
  }
}

function handlePhotoSelect(input) {
  const file = input.files[0];
  const uploadDiv = document.querySelector('.photo-upload');
  
  if (file) {
    const reader = new FileReader();
    reader.onload = function(e) {
      uploadDiv.style.backgroundImage = `url(${e.target.result})`;
      uploadDiv.classList.add('has-photo');
    };
    reader.readAsDataURL(file);
  }
}

// ── Toggle type de vidéo ──
function toggleVideoType(type) {
  const uploadSection = document.getElementById('upload-section');
  const youtubeSection = document.getElementById('youtube-section');
  
  if (type === 'upload') {
    uploadSection.style.display = 'block';
    youtubeSection.style.display = 'none';
  } else {
    uploadSection.style.display = 'none';
    youtubeSection.style.display = 'block';
  }
}

// ── Recherche d'artiste ──
function initArtisteSearch() {
  const searchInput = document.getElementById('search-artiste');
  if (!searchInput) return;
  
  searchInput.addEventListener('input', function(e) {
    const searchTerm = e.target.value.toLowerCase();
    const artisteCards = document.querySelectorAll('.artiste-card');
    
    artisteCards.forEach(card => {
      const nomArtiste = card.querySelector('.artiste-nom')?.textContent.toLowerCase() || '';
      if (nomArtiste.includes(searchTerm)) {
        card.style.display = '';
      } else {
        card.style.display = 'none';
      }
    });
  });
}

// ── Initialisation au chargement ──
document.addEventListener('DOMContentLoaded', function() {
  initArtisteSearch();
});
