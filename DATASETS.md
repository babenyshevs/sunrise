* cust_details.csv: contains potentially relevant information about internet customers during an adequate time period for every customer who requested a Wi-Fi booster, and a representative sample of customers without a booster.
	Column description
	- customer_id: a surrogate key uniquely identifying customers. No purpose or meaning other than identification.
	- zip: The first digit of the ZIP code corresponding to the customer's home location.
	- commune: Encoding population density around the customer's home location. Can be either "urban" or "rural".
	- gender: Customer's gender. Can be either "f" or "m".
	- dob: Customer's date of birth. Format: "yyyy-mm-dd"
	- tenure: Total number of months the customer's subscription has been active.
	- internet_usage: Encoding how heavily the customer is using their internet subscription. Can be "Low", "Medium", "High" or "Extreme".
	- tv_product: Encoding the quality rank of the customer's TV subscription. Can be "Low", "Medium" or "High". Optional, with missing values indicating no TV product.
	- mobile_product: Encoding the quality rank of the customer's mobile phone subscription. Can be "Low", "Medium" or "High". Optional, with missing values indicating no mobile phone product.

* SuperBooster.csv: contains a list of customer_ids who have asked for, received, and are using SuperBooster™

* cancellations.csv: contains a list of customer_ids who have cancelled their subscription during the observed time period