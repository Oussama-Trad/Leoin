package com.leoni.services;

import com.leoni.models.News;
import com.leoni.models.Admin;
import com.leoni.models.SuperAdmin;
import com.leoni.repositories.NewsRepository;
import com.leoni.repositories.AdminRepository;
import com.leoni.repositories.SuperAdminRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class NewsService {
    
    @Autowired
    private NewsRepository newsRepository;
    
    @Autowired
    private AdminRepository adminRepository;
    
    @Autowired
    private SuperAdminRepository superAdminRepository;
    
    /**
     * Create a new news article
     */
    public News createNews(News news, String authorId, String authorType) {
        // Set author information based on type
        if ("ADMIN".equals(authorType)) {
            Optional<Admin> admin = adminRepository.findById(authorId);
            if (admin.isPresent()) {
                Admin adminUser = admin.get();
                news.setAuthorRef(adminUser.getId());
                news.setAuthorName(adminUser.getUsername());
                news.setTargetLocation(adminUser.getLocation());
                news.setTargetDepartment(adminUser.getDepartment());
            }
        } else if ("SUPERADMIN".equals(authorType)) {
            Optional<SuperAdmin> superAdmin = superAdminRepository.findById(authorId);
            if (superAdmin.isPresent()) {
                SuperAdmin superAdminUser = superAdmin.get();
                news.setAuthorRef(superAdminUser.getId());
                news.setAuthorName(superAdminUser.getUsername());
                // SuperAdmin can target any location/department
                // These will be set via the request parameters
            }
        }
        
        news.setCreatedAt(LocalDateTime.now());
        news.setUpdatedAt(LocalDateTime.now());
        
        return newsRepository.save(news);
    }
    
    /**
     * Get news for a specific user based on their location and department
     */
    public List<News> getNewsForUser(String userLocation, String userDepartment) {
        // Use legacy format directly (isActive)
        return newsRepository.findActiveNewsByLocationAndDepartment(userLocation, userDepartment);
    }
    
    /**
     * Get news for admin - only their targeted location and department
     */
    public List<News> getNewsForAdmin(String adminId) {
        Optional<Admin> admin = adminRepository.findById(adminId);
        if (admin.isPresent()) {
            Admin adminUser = admin.get();
            // Use legacy format directly (isActive)
            return newsRepository.findActiveNewsByLocationAndDepartment(
                adminUser.getLocation(), 
                adminUser.getDepartment()
            );
        }
        return List.of();
    }
    
    /**
     * Get all news for superadmin with optional filtering
     */
    public List<News> getAllNewsForSuperAdmin() {
        // Use legacy format directly (isActive)
        return newsRepository.findAllActiveNews();
    }
    
    /**
     * Get ALL news regardless of status - for debugging
     */
    public List<News> getAllNews() {
        return newsRepository.findAll();
    }
    
    /**
     * Get news by author
     */
    public List<News> getNewsByAuthor(String authorId) {
        return newsRepository.findByAuthorRef(authorId);
    }
    
    /**
     * Update news
     */
    public News updateNews(String newsId, News updatedNews) {
        Optional<News> existingNews = newsRepository.findById(newsId);
        if (existingNews.isPresent()) {
            News news = existingNews.get();
            news.setTitle(updatedNews.getTitle());
            news.setContent(updatedNews.getContent());
            news.setSummary(updatedNews.getSummary());
            news.setCategory(updatedNews.getCategory());
            news.setPriority(updatedNews.getPriority());
            news.setUpdatedAt(LocalDateTime.now());
            
            // Allow updating target location/department for superadmin
            if (updatedNews.getTargetLocation() != null) {
                news.setTargetLocation(updatedNews.getTargetLocation());
            }
            if (updatedNews.getTargetDepartment() != null) {
                news.setTargetDepartment(updatedNews.getTargetDepartment());
            }
            
            return newsRepository.save(news);
        }
        return null;
    }
    
    /**
     * Publish news
     */
    public News publishNews(String newsId) {
        Optional<News> existingNews = newsRepository.findById(newsId);
        if (existingNews.isPresent()) {
            News news = existingNews.get();
            news.publish();
            return newsRepository.save(news);
        }
        return null;
    }
    
    /**
     * Archive news
     */
    public News archiveNews(String newsId) {
        Optional<News> existingNews = newsRepository.findById(newsId);
        if (existingNews.isPresent()) {
            News news = existingNews.get();
            news.archive();
            return newsRepository.save(news);
        }
        return null;
    }
    
    /**
     * Delete news
     */
    public boolean deleteNews(String newsId) {
        if (newsRepository.existsById(newsId)) {
            newsRepository.deleteById(newsId);
            return true;
        }
        return false;
    }
    
    /**
     * Get news by ID
     */
    public Optional<News> getNewsById(String newsId) {
        return newsRepository.findById(newsId);
    }
    
    /**
     * Get filtered news based ONLY on location and department
     */
    public List<News> getFilteredNews(String location, String department) {
        System.out.println("=== FILTERING NEWS ===");
        System.out.println("Location filter: '" + location + "'");
        System.out.println("Department filter: '" + department + "'");
        
        // Start with all active news
        List<News> news = newsRepository.findAllActiveNews();
        System.out.println("Total active news found: " + news.size());
        
        // Apply location filter if provided
        if (location != null && !location.trim().isEmpty()) {
            news = news.stream()
                .filter(n -> location.equalsIgnoreCase(n.getTargetLocation()))
                .toList();
            System.out.println("After location filter: " + news.size());
        }
        
        // Apply department filter if provided
        if (department != null && !department.trim().isEmpty()) {
            news = news.stream()
                .filter(n -> department.equalsIgnoreCase(n.getTargetDepartment()))
                .toList();
            System.out.println("After department filter: " + news.size());
        }
        
        System.out.println("Final filtered news count: " + news.size());
        return news;
    }
}
