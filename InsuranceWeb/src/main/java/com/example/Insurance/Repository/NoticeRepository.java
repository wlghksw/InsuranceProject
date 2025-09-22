package com.example.Insurance.Repository;

import com.example.Insurance.Entity.Notice;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface NoticeRepository extends JpaRepository<Notice, Long> {
    // 최신 공지사항이 위로 오도록 ID를 기준으로 내림차순 정렬
    List<Notice> findAllByOrderByIdDesc();
}
