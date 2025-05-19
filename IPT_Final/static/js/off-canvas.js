document.addEventListener('DOMContentLoaded', function() {
    // Get the sidebar toggle button and sidebar element
    const sidebarToggle = document.querySelector('[data-toggle="minimize"]');
    const sidebar = document.querySelector('.sidebar');
    const mainPanel = document.querySelector('.main-panel');
    const body = document.body;
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Toggle sidebar on mobile
            if (window.innerWidth <= 991) {
                sidebar.classList.toggle('active');
            }
            // Toggle sidebar on desktop
            else {
                if (sidebar.style.width === '70px') {
                    sidebar.style.width = '260px';
                    mainPanel.style.width = 'calc(100% - 260px)';
                    body.classList.remove('sidebar-closed');
                    
                    // Show full logo
                    document.querySelector('.navbar-brand').style.display = 'block';
                    document.querySelector('.brand-logo-mini').style.display = 'none';
                    
                    // Show menu titles
                    document.querySelectorAll('.menu-title').forEach(title => {
                        title.style.display = 'block';
                    });
                } else {
                    sidebar.style.width = '70px';
                    mainPanel.style.width = 'calc(100% - 70px)';
                    body.classList.add('sidebar-closed');
                    
                    // Show mini logo
                    document.querySelector('.navbar-brand').style.display = 'none';
                    document.querySelector('.brand-logo-mini').style.display = 'block';
                    
                    // Hide menu titles
                    document.querySelectorAll('.menu-title').forEach(title => {
                        title.style.display = 'none';
                    });
                }
            }
        });
    }
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 991 && 
            !sidebar.contains(e.target) && 
            !e.target.closest('[data-toggle="minimize"]')) {
            sidebar.classList.remove('active');
        }
    });
}); 