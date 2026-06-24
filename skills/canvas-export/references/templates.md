# Canvas Quiz Export — XML Templates

## imsmanifest.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="[MANIFEST-GUID]"
  xmlns="http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1"
  xmlns:lom="http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource"
  xmlns:imsmd="http://www.imsglobal.org/xsd/imsmd_v1p2"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1 http://www.imsglobal.org/xsd/imscp_v1p1.xsd http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource http://www.imsglobal.org/profile/cc/ccv1p1/LOM/ccv1p1_lomresource_v1p0.xsd http://www.imsglobal.org/xsd/imsmd_v1p2 http://www.imsglobal.org/xsd/imsmd_v1p2p2.xsd">
  <metadata>
    <schema>IMS Content</schema>
    <schemaversion>1.1.3</schemaversion>
    <imsmd:lom>
      <imsmd:general>
        <imsmd:title>
          <imsmd:string>[Package Title]</imsmd:string>
        </imsmd:title>
      </imsmd:general>
      <imsmd:lifeCycle>
        <imsmd:contribute>
          <imsmd:date>
            <imsmd:dateTime>[YYYY-MM-DD]</imsmd:dateTime>
          </imsmd:date>
        </imsmd:contribute>
      </imsmd:lifeCycle>
      <imsmd:rights>
        <imsmd:copyrightAndOtherRestrictions>
          <imsmd:value>yes</imsmd:value>
        </imsmd:copyrightAndOtherRestrictions>
        <imsmd:description>
          <imsmd:string>Private (Copyrighted) - http://en.wikipedia.org/wiki/Copyright</imsmd:string>
        </imsmd:description>
      </imsmd:rights>
    </imsmd:lom>
  </metadata>
  <organizations/>
  <resources>
    <!-- Repeat this block for each quiz -->
    <resource identifier="[QUIZ-GUID]" type="imsqti_xmlv1p2">
      <file href="[QUIZ-GUID]/[QUIZ-GUID].xml"/>
      <dependency identifierref="[DEP-GUID]"/>
    </resource>
    <resource identifier="[DEP-GUID]"
      type="associatedcontent/imscc_xmlv1p1/learning-application-resource"
      href="[QUIZ-GUID]/assessment_meta.xml">
      <file href="[QUIZ-GUID]/assessment_meta.xml"/>
    </resource>
  </resources>
</manifest>
```

**Standalone folder manifest** (when `imsmanifest.xml` lives *inside* `[QUIZ-GUID]/`):
Change file hrefs to just `[QUIZ-GUID].xml` and `assessment_meta.xml` — no subfolder prefix.

---

## assessment_meta.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<quiz identifier="[QUIZ-GUID]"
  xmlns="http://canvas.instructure.com/xsd/cccv1p0"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd">
  <title>[Quiz Title]</title>
  <description>&lt;div class="description user_content teacher-version enhanced"&gt;
&lt;p&gt;[Quiz description here.]&lt;/p&gt;
&lt;/div&gt;</description>
  <due_at>[ISO8601 or empty]</due_at>
  <lock_at>[ISO8601 or empty]</lock_at>
  <unlock_at/>
  <shuffle_answers>false</shuffle_answers>
  <scoring_policy>keep_highest</scoring_policy>
  <hide_results></hide_results>
  <quiz_type>assignment</quiz_type>
  <points_possible>[TOTAL_POINTS].0</points_possible>
  <require_lockdown_browser>false</require_lockdown_browser>
  <require_lockdown_browser_for_results>false</require_lockdown_browser_for_results>
  <require_lockdown_browser_monitor>false</require_lockdown_browser_monitor>
  <lockdown_browser_monitor_data></lockdown_browser_monitor_data>
  <show_correct_answers>false</show_correct_answers>
  <anonymous_submissions>false</anonymous_submissions>
  <could_be_locked>true</could_be_locked>
  <time_limit>[MINUTES]</time_limit>
  <disable_timer_autosubmission>false</disable_timer_autosubmission>
  <allowed_attempts>1</allowed_attempts>
  <one_question_at_a_time>false</one_question_at_a_time>
  <cant_go_back>false</cant_go_back>
  <available>true</available>
  <one_time_results>false</one_time_results>
  <show_correct_answers_last_attempt>false</show_correct_answers_last_attempt>
  <only_visible_to_overrides>false</only_visible_to_overrides>
  <module_locked>false</module_locked>
  <assignment identifier="[ASSIGNMENT-GUID]">
    <title>[Quiz Title]</title>
    <due_at>[ISO8601 or empty]</due_at>
    <lock_at>[ISO8601 or empty]</lock_at>
    <unlock_at/>
    <module_locked>false</module_locked>
    <workflow_state>unpublished</workflow_state>
    <assignment_overrides>
    </assignment_overrides>
    <quiz_identifierref>[QUIZ-GUID]</quiz_identifierref>
    <allowed_extensions></allowed_extensions>
    <has_group_category>false</has_group_category>
    <points_possible>[TOTAL_POINTS].0</points_possible>
    <grading_type>points</grading_type>
    <all_day>false</all_day>
    <submission_types>online_quiz</submission_types>
    <position>1</position>
    <turnitin_enabled>false</turnitin_enabled>
    <vericite_enabled>false</vericite_enabled>
    <peer_review_count>0</peer_review_count>
    <peer_reviews>false</peer_reviews>
    <automatic_peer_reviews>false</automatic_peer_reviews>
    <anonymous_peer_reviews>false</anonymous_peer_reviews>
    <grade_group_students_individually>false</grade_group_students_individually>
    <freeze_on_copy>false</freeze_on_copy>
    <omit_from_final_grade>false</omit_from_final_grade>
    <hide_in_gradebook>false</hide_in_gradebook>
    <intra_group_peer_reviews>false</intra_group_peer_reviews>
    <only_visible_to_overrides>false</only_visible_to_overrides>
    <post_to_sis>false</post_to_sis>
    <moderated_grading>false</moderated_grading>
    <grader_count>0</grader_count>
    <grader_comments_visible_to_graders>true</grader_comments_visible_to_graders>
    <anonymous_grading>false</anonymous_grading>
    <graders_anonymous_to_graders>false</graders_anonymous_to_graders>
    <grader_names_visible_to_final_grader>true</grader_names_visible_to_final_grader>
    <anonymous_instructor_annotations>false</anonymous_instructor_annotations>
    <post_policy>
      <post_manually>false</post_manually>
    </post_policy>
  </assignment>
  <assignment_group_identifierref>gc068f0165ae280ed0205b233203e5a67</assignment_group_identifierref>
  <assignment_overrides>
  </assignment_overrides>
</quiz>
```

---

## QTI — True/False Question

```xml
<item ident="[ITEM-GUID]" title="Question">
  <itemmetadata>
    <qtimetadata>
      <qtimetadatafield>
        <fieldlabel>question_type</fieldlabel>
        <fieldentry>true_false_question</fieldentry>
      </qtimetadatafield>
      <qtimetadatafield>
        <fieldlabel>points_possible</fieldlabel>
        <fieldentry>2.0</fieldentry>
      </qtimetadatafield>
      <qtimetadatafield>
        <fieldlabel>original_answer_ids</fieldlabel>
        <fieldentry>[N]100,[N]200</fieldentry>
      </qtimetadatafield>
      <qtimetadatafield>
        <fieldlabel>assessment_question_identifierref</fieldlabel>
        <fieldentry>[AQ-GUID]</fieldentry>
      </qtimetadatafield>
    </qtimetadata>
  </itemmetadata>
  <presentation>
    <material>
      <mattext texttype="text/html">&lt;div&gt;[Question text — HTML-encode quotes as &amp;amp;quot;]&lt;/div&gt;</mattext>
    </material>
    <response_lid ident="response1" rcardinality="Single">
      <render_choice>
        <response_label ident="[N]100">
          <material>
            <mattext texttype="text/plain">True</mattext>
          </material>
        </response_label>
        <response_label ident="[N]200">
          <material>
            <mattext texttype="text/plain">False</mattext>
          </material>
        </response_label>
      </render_choice>
    </response_lid>
  </presentation>
  <resprocessing>
    <outcomes>
      <decvar maxvalue="100" minvalue="0" varname="SCORE" vartype="Decimal"/>
    </outcomes>
    <respcondition continue="No">
      <conditionvar>
        <!-- Use [N]100 if answer is True, [N]200 if answer is False -->
        <varequal respident="response1">[CORRECT-IDENT]</varequal>
      </conditionvar>
      <setvar action="Set" varname="SCORE">100</setvar>
    </respcondition>
  </resprocessing>
</item>
```

---

## QTI — Multiple Choice Question (4 options)

```xml
<item ident="[ITEM-GUID]" title="Question">
  <itemmetadata>
    <qtimetadata>
      <qtimetadatafield>
        <fieldlabel>question_type</fieldlabel>
        <fieldentry>multiple_choice_question</fieldentry>
      </qtimetadatafield>
      <qtimetadatafield>
        <fieldlabel>points_possible</fieldlabel>
        <fieldentry>2.0</fieldentry>
      </qtimetadatafield>
      <qtimetadatafield>
        <fieldlabel>original_answer_ids</fieldlabel>
        <fieldentry>[N]100,[N]200,[N]300,[N]400</fieldentry>
      </qtimetadatafield>
      <qtimetadatafield>
        <fieldlabel>assessment_question_identifierref</fieldlabel>
        <fieldentry>[AQ-GUID]</fieldentry>
      </qtimetadatafield>
    </qtimetadata>
  </itemmetadata>
  <presentation>
    <material>
      <mattext texttype="text/html">&lt;div&gt;[Question text]&lt;/div&gt;</mattext>
    </material>
    <response_lid ident="response1" rcardinality="Single">
      <render_choice>
        <response_label ident="[N]100">
          <material>
            <mattext texttype="text/plain">[Option A text]</mattext>
          </material>
        </response_label>
        <response_label ident="[N]200">
          <material>
            <mattext texttype="text/plain">[Option B text]</mattext>
          </material>
        </response_label>
        <response_label ident="[N]300">
          <material>
            <mattext texttype="text/plain">[Option C text]</mattext>
          </material>
        </response_label>
        <response_label ident="[N]400">
          <material>
            <mattext texttype="text/plain">[Option D text]</mattext>
          </material>
        </response_label>
      </render_choice>
    </response_lid>
  </presentation>
  <resprocessing>
    <outcomes>
      <decvar maxvalue="100" minvalue="0" varname="SCORE" vartype="Decimal"/>
    </outcomes>
    <respcondition continue="No">
      <conditionvar>
        <!-- Ident of the correct option -->
        <varequal respident="response1">[CORRECT-IDENT]</varequal>
      </conditionvar>
      <setvar action="Set" varname="SCORE">100</setvar>
    </respcondition>
  </resprocessing>
</item>
```
