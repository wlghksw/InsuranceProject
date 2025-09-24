package com.example.Insurance.DTO;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class UserDTO {

    @NotBlank(message = "아이디는 필수 입력값입니다.")
    @Size(min = 4, max = 20, message = "아이디는 4자 이상 20자 이하로 입력해주세요.")
    private String loginId;

    @NotBlank(message = "비밀번호는 필수 입력값입니다.")
    @Pattern(regexp = "^(?=.*[A-Za-z])(?=.*\\d)(?=.*[@$!%*#?&])[A-Za-z\\d@$!%*#?&]{8,}$",
            message = "비밀번호는 8자 이상, 영문, 숫자, 특수문자를 포함해야 합니다.")
    private String password;

    @NotBlank(message = "닉네임은 필수 입력값입니다.")
    private String nickname;

    @NotBlank(message = "이름은 필수 입력값입니다.")
    private String realName;

    @NotBlank(message = "전화번호는 필수 입력값입니다.")
    @Pattern(regexp = "^\\d{10,11}$", message = "올바른 전화번호를 입력해주세요.")
    private String phone;

    @NotBlank(message = "출생년도는 필수 입력값입니다.")
    @Pattern(regexp = "^\\d{4}$", message = "출생년도 4자리를 입력해주세요.")
    private String birthYear;

    @NotBlank(message = "성별은 필수 입력값입니다.")
    // 성별은 Enum을 사용하는 것이 더 좋지만, 예시를 위해 String으로 남겨둡니다.
    private String gender;

    private String profileImage;
}
