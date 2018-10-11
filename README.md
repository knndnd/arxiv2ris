# arxiv2ris

This script runs using Python 3.

First, install the required packages. This script only requires ``nltk`` and ``PyEnchant``.

```bash
$ pip3 install -r requirements.txt
```

If you run the error that the package ``punkt`` doesn't exist, download it by going into your Python environment and running:

```bash
$ python3

>>> import nltk
>>> nltk.download('punkt')
```

In MacOS, you can get the SSL error

```
[nltk_data] Error loading punkt: <urlopen error [SSL:
[nltk_data]     CERTIFICATE_VERIFY_FAILED] certificate verify failed:
[nltk_data]     unable to get local issuer certificate (_ssl.c:1045)>
```

this will be fixed by reinstalling certificates
```shell
$ /Applications/Python\ 3.x/Install\ Certificates.command
```


To query for a certain keyword, run:

Usage: arxiv2ris -h {-n number} {-t dateoption} {-f fieldoption} -k "keywords1 keywords2 " 
	-h  help
	-n  number of references
	-f  fields to be searched, the fields can be:
		a         :   all
		t         :   title
		b         :   abstract
		i         :   paper_id
		u         :   author   
	-t  date range   
		a         :     'all_dates'
		p         :     'past_12',    past 12 months
		y         :     'specific_year'

	-y  2018, or other year
	-k  "keywords"

The result will be written to a local file "tmp.ris", with the following format:

TY  - Preprint
T1  - Semi-supervised Deep Reinforcement Learning in Support of IoT and Smart City Services
A1  - Mehdi Mohammadi
A1  - Ala Al-Fuqaha
A1  - Mohsen Guizani
A1  - Jun-Seok Oh
JO  - ArXiv e-prints
Y1  - 9 October, 2018
UR  - https://arxiv.org/abs/1810.04118
N2  - Smart services are an important element of the smart cities and the Internet of Things (IoT) ecosystems where the intelligence behind the services is obtained and improved through the sensory data. Providing a large amount of training data is not always feasible; therefore, we need to consider alternative ways that incorporate unlabeled data as well. In recent years, Deep reinforcement learning (DRL) has gained great success in several application domains. It is an applicable method for IoT and smart city scenarios where auto-generated data can be partially labeled by users&#39; feedback for training purposes. In this paper, we propose a semi-supervised deep reinforcement learning model that fits smart city applications as it consumes both labeled and unlabeled data to improve the performance and accuracy of the learning agent. The model utilizes Variational Autoencoders (VAE) as the inference engine for generalizing optimal policies. To the best of our knowledge, the proposed model is the first investigation that extends deep reinforcement learning to the semi-supervised paradigm. As a case study of smart city applications, we focus on smart buildings and apply the proposed model to the problem of indoor localization based on BLE signal strength. Indoor localization is the main component of smart city services since people spend significant time in indoor environments. Our model learns the best action policies that lead to a close estimation of the target locations with an improvement of 23% in terms of distance to the target and at least 67% more received rewards compared to the supervised DRL model.
ER  -

Users can double click the file tmp.ris to import it to Endnote.
