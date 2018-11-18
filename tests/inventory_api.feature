Feature: Test the REST entrypoints of the inventory api

  Scenario: The register new product entrypoint accepts new entries
    When the entrypoint to register a new product receives the following data
      | name    |
      | chicken |
    Then the response is accepted and contains the following name
      | name    |
      | chicken |

  Scenario: We can retrieve the list of products in the system
    When the following products are added
      | name    |
      | chicken |
      | noodles |
      | beans   |
    Then the list of products in the system contains the following names
      | name    |
      | chicken |
      | noodles |
      | beans   |

  Scenario: We can add batches in the warehouse and read them by product
    Given the following products in the system
      | name    |
      | chicken |
      | noodles |
      | beans   |
    When a new batch with "3" items of "chicken" is added with expiry date for "tomorrow"
    And a new batch with "2" items of "chicken" is added with expiry date for "next week"
    Then the list of batches of "chicken" contains the following
      | stock:int | expiry_date:date_str |
      | 3         | tomorrow             |
      | 2         | next week            |

  Scenario: We can modify the stock of a batch
    Given the following products in the system
      | name    |
      | chicken |
      | noodles |
      | beans   |
    And there is a batch with "3" items of "chicken" and expiry date for "next week"
    When the stock of the previously created stock is updated to "2"
    Then the list of batches of "chicken" contains the following
      | stock:int | expiry_date:date_str |
      | 2         | next week            |
