Feature: Overview entrypoints

  Background: Common steps
    Given the following products in the system
      | name    |
      | chicken |
      | noodles |
      | beans   |
    And there is a batch with "10" items of "chicken" and expiry date for "yesterday"
    And there is a batch with "1" items of "chicken" and expiry date for "today"
    And there is a batch with "4" items of "chicken" and expiry date for "tomorrow"
    And there is a batch with "7" items of "chicken" and expiry date for "in 7 days"
    And there is a batch with "1" items of "chicken" and expiry date for "in 20 days"

  Scenario: We can read FRESH batches
    When the list of "FRESH" batches is requested
    Then the response is ok and the following batches are returned
      | stock:int | expiry_date:date_str |
      | 7         | in 7 days            |
      | 1         | in 20 days           |

  Scenario: We can read EXPIRED batches
    When the list of "EXPIRED" batches is requested
    Then the response is ok and the following batches are returned
      | stock:int | expiry_date:date_str |
      | 10        | yesterday            |

  Scenario: We can read EXPIRING batches
    When the list of "EXPIRING" batches is requested
    Then the response is ok and the following batches are returned
      | stock:int | expiry_date:date_str |
      | 1         | today                |
      | 4         | tomorrow             |
