package com.example.Insurance.Service;

import com.example.Insurance.Entity.Notice;
import com.example.Insurance.Repository.NoticeRepository;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class NoticeService {

    private final NoticeRepository noticeRepository;

    public NoticeService(NoticeRepository noticeRepository) {
        this.noticeRepository = noticeRepository;
    }

    public List<Notice> findAllNotices() {
        return noticeRepository.findAllByOrderByIdDesc();
    }
}
