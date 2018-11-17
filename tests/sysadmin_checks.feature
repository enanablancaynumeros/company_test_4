Feature: Microservice is ok for sys admins

  Scenario: The microservice health is ok
    When we go to the internal health endpoint of the paidsearch API
    Then the response of the microservice is "{"msg": "ok"}"
