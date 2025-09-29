
package com.example.Insurance.DTO;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;


@Getter
@Setter
public class AccidentRecommendationRequest {

    @JsonProperty("age")
    private int age;

    @JsonProperty("sex")
    private String sex;

    @JsonProperty("top_n")
    private int topN;

    @JsonProperty("sort_by")
    private String sortBy;


}