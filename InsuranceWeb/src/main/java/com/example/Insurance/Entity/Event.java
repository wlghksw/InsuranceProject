package com.example.Insurance.Entity;

import java.time.LocalDate;

public class Event {
    private Long id;
    private String title;
    private String summary;
    private String imageUrl;
    private LocalDate startDate;
    private LocalDate endDate;

    public Event() {}

    public Event(Long id, String title, String summary, String imageUrl,
                 LocalDate startDate, LocalDate endDate) {
        this.id = id;
        this.title = title;
        this.summary = summary;
        this.imageUrl = imageUrl;
        this.startDate = startDate;
        this.endDate = endDate;
    }

    public Long getId() { return id; }
    public String getTitle() { return title; }
    public String getSummary() { return summary; }
    public String getImageUrl() { return imageUrl; }
    public LocalDate getStartDate() { return startDate; }
    public LocalDate getEndDate() { return endDate; }

    public void setId(Long id) { this.id = id; }
    public void setTitle(String title) { this.title = title; }
    public void setSummary(String summary) { this.summary = summary; }
    public void setImageUrl(String imageUrl) { this.imageUrl = imageUrl; }
    public void setStartDate(LocalDate startDate) { this.startDate = startDate; }
    public void setEndDate(LocalDate endDate) { this.endDate = endDate; }
}
