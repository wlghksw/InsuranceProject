package com.example.Insurance.board;

import com.example.Insurance.Entity.Event;
import jakarta.annotation.PostConstruct;
import org.springframework.stereotype.Component;

import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

@Component
public class EventMemoryStore {

    private final List<Event> posts = new ArrayList<>();

    @PostConstruct
    public void init() {
        posts.add(new Event(18L, "다시 돌아온 스타벅스 기프티콘 이벤트", "교육 듣고 기프티콘도 받고 일석이조!",
                "/images/ojc-event18.png",
                LocalDate.of(2024,4,15), LocalDate.of(2024,6,30)));

        posts.add(new Event(17L, "야간반&주말반 수강후기 이벤트", "7,8,9월 수강자 후기를 남겨주세요!",
                "/images/ojc-event17.jpg",
                LocalDate.of(2023,7,1), LocalDate.of(2023,9,30)));

        posts.add(new Event(16L, "7,8월 일반과정&비환급대상자 이벤트", "국비지 못받는다고? 걱정말 30% 할인받자!",
                "/images/ojc-event16.jpg",
                LocalDate.of(2023,7,1), LocalDate.of(2023,8,31)));

        posts.add(new Event(15L, "오라클자바교육학원 10주년 이벤트", "10주년 이벤트에 참여하고 준비한 선물받자!",
                "/images/ojc-event15.jpg",
                LocalDate.of(2023,2,1), LocalDate.of(2023,3,31)));

        posts.add(new Event(14L, "8 & 9월 야간과정 수강 이벤트", "8월 & 9월 야간반 수강 후 수료하고 피자 기프티콘 받자!",
                "/images/ojc-event14.jpg",
                LocalDate.of(2022,8,1), LocalDate.of(2022,9,30)));

        posts.add(new Event(13L, "[오라클자바교육센터] 신규과정 런칭 이벤트", "신규과정 들으면 스타벅스 기프티콘이!",
                "/images/ojc-event13.jpg",
                LocalDate.of(2022,7,1), LocalDate.of(2022,9,30)));

        posts.add(new Event(12L, "7월 신규과정 런칭 무료세미나", "",
                "/images/ojc-event12.jpg",
                LocalDate.of(2021,7,10), LocalDate.of(2021,7,10)));

        posts.add(new Event(11L, "7월 야간과정 수강 이벤트", "7월 야간반 수업듣고 휴대폰무선충전기 받아가자!",
                "/images/ojc-event11.jpg",
                LocalDate.of(2021,6,22), LocalDate.of(2021,8,31)));

        posts.add(new Event(10L, "BEST 수강후기 이벤트", "수강후기 쓰고 StarBucks 기프티콘 받자!",
                "/images/ojc-event10.jpg",
                LocalDate.of(2021,4,1), LocalDate.of(2021,6,30)));

        posts.add(new Event(9L, "MSP,PMP 수강신청하고 무료로 점심먹자!", "[평일반]프로젝트 관리과정을 신청해주시면 모든분들께 식사쿠폰을 드립니다!",
                "/images/ojc-event9.jpg",
                LocalDate.of(2021,1,20), LocalDate.of(2021,12,31)));

        posts.add(new Event(8L, "2020년 저녁반 수강생들을 위한 스타벅스 이벤트!", "야간수업 듣고, StarBucks 커피 쿠폰 받자!",
                "/images/ojc-event8.jpg",
                LocalDate.of(2020,1,13), LocalDate.of(2020,3,31)));

        posts.add(new Event(7L, "저녁반 수강생들을 위한 스타벅스 이벤트!", "수강후기를 작성해 주시면 모든 수강생들에게 스타벅스 커피를 드립니다!",
                "/images/ojc-event7.jpg",
                LocalDate.of(2019,10,25), LocalDate.of(2019,12,31)));

        posts.add(new Event(6L, "수강후기 포스팅하면 스타벅스 커피가 무료! 100% 증정", "홈페이지 오픈기념 교육후기 리뷰왕 이벤트!",
                "/images/ojc-event6.jpg",
                LocalDate.of(2019,7,1), LocalDate.of(2019,9,30)));

        posts.add(new Event(5L, "MSP 실무과정 수강생 점심식사 제공", "MSP 실무과정을 수강하시는 모든 수강생분들을 대상으로 하는 점심식사 제공 이벤트!",
                "/images/ojc-event5.jpg",
                LocalDate.of(2019,2,13), LocalDate.of(2019,12,31)));

        posts.add(new Event(4L, "카카오 플러스친구 등록하면 교육비 할인권을 드립니다.", "@오라클자바교육센터를 친구추가 하세요!! 친구 모두에게 본인부담금 힐인권을 100% 쏩니다!!",
                "/images/ojc-event4.jpg",
                LocalDate.of(2017,6,9), LocalDate.of(2017,7,31)));

        posts.add(new Event(3L, "오라클자바교육센터 SNS 홍보 이벤트 ", "교육후기, 과정내용, 위치정보 등 다양한 주제를 통해 홍보를 진행해주시면 됩니다.",
                "/images/ojc-event3.gif",
                LocalDate.of(2017,6,1), LocalDate.of(2017,7,31)));

        posts.add(new Event(2L, "근로자카드 본인부담금 더 이상 부담 갖지 말자!", "3월 야간/주말 본인부담금 대/폭/할/인 이벤트 진행! 지금 확인하세요!",
                "/images/ojc-event2.jpg",
                LocalDate.of(2017,3,7), LocalDate.of(2017,3,31)));

        posts.add(new Event(1L, "오라클자바교육센터 미환급자 이벤트", "오라클자바교육센터 미환급자 이벤트",
                "/images/ojc-event1.jpg",
                LocalDate.of(2017,2,3), LocalDate.of(2018,2,4)));

    }

    public List<Event> findAllDesc() {
        return posts.stream()
                .sorted(Comparator.comparing(Event::getId).reversed())
                .collect(Collectors.toList());
    }

    public Optional<Event> findById(Long id) {
        return posts.stream().filter(p -> Objects.equals(p.getId(), id)).findFirst();
    }
}
