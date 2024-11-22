document.addEventListener('DOMContentLoaded', () => {
    const searchIcon = document.getElementById('searchIcon');
    const searchForm = document.getElementById('searchForm');

    searchIcon.addEventListener('click', () => {
        searchForm.classList.toggle('active');
    });
});