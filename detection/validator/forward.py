# The MIT License (MIT)
 # Copyright © 2024 It's AI
import random

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import bittensor as bt
import numpy as np

from detection.protocol import TextSynapse
from detection.validator.data_augmentation import DataAugmentator
from detection.validator.models import ValDataRow
from detection.validator.reward import get_rewards
from detection.utils.uids import get_random_uids
from detection.validator.generate_version import generate_random_version

from detection import __version__

import time
from typing import List
import torch


async def get_all_responses(self, axons, texts: List[ValDataRow], check_ids, timeout, step=35, min_text_length=250):
    all_responses = []
    version_responses = []    
    check_responses = []
    augmentator = DataAugmentator()
    for i in range(0, len(axons), step):
        bt.logging.info(f"Sending challenges to the #{i} subset of miners with size {step}")
        subset_axons = axons[i:i + step]

        auged_texts = []
        for el in texts:
            text_auged, augs = augmentator(el.text)
            if len(text_auged) >= min_text_length:
                auged_texts.append(text_auged)
            else:
                auged_texts.append(el.text_auged)

        responses: List[TextSynapse] = await self.dendrite(
            axons=subset_axons,
            synapse=TextSynapse(
                texts=[auged_texts[idx] for idx in check_ids],
                predictions=[],
                version=__version__
            ),
            deserialize=True,
            timeout=timeout,
        )
        check_responses.extend(responses)

        random_version = generate_random_version(
                self.version, self.least_acceptable_version)

        responses: List[TextSynapse] = await self.dendrite(
            axons=subset_axons,
            synapse=TextSynapse(
                texts=auged_texts,
                predictions=[],
                version=random_version
            ),
            deserialize=True,
            timeout=timeout,
        )
        version_responses.extend(responses)

        responses: List[TextSynapse] = await self.dendrite(
            axons=subset_axons,
            synapse=TextSynapse(
                texts=auged_texts,
                predictions=[],
                version=__version__ 
            ),
            deserialize=True,
            timeout=timeout,
        )
        all_responses.extend(responses)

        # Log the results for monitoring purposes.
        bt.logging.info(f"Received responses: {len(responses)}")
        bt.logging.info(f"Overall amount of responses: {len(all_responses)}")
    return all_responses, check_responses, version_responses


async def forward(self):
    """
    The forward function is called by the validator every time step.

    It is responsible for querying the network and scoring the responses.

    Args:
        self (:obj:`bittensor.neuron.Neuron`): The neuron object which contains all the necessary state for the validator.

    """
    bt.logging.info("Updating and querying available uids")
    # Define how the validator selects a miner to query, how often, etc.
    # bt.logging.info(f"STEPS {self.step} {self.step%300} {not (self.step % 300)}")

    available_axon_size = len(self.metagraph.axons) - 1 # Except our own
    miner_selection_size = min(available_axon_size, self.config.neuron.sample_size)
    miner_uids = get_random_uids(self, k=miner_selection_size)
    axons = [self.metagraph.axons[uid] for uid in miner_uids]

    start_time = time.time()
    texts, labels = await self.build_queries()
    end_time = time.time()
    bt.logging.info(f"Time to generate challenges: {int(end_time - start_time)}")

    cnt_challenges_for_check = random.randint(1, min(10, len(texts)))
    check_ids = np.random.choice(np.arange(len(texts)).astype(int), size=cnt_challenges_for_check, replace=False)

    all_responses, check_responses,  version_responses = await get_all_responses(
        self, axons, texts, check_ids, self.config.neuron.timeout)

    rewards, metrics = get_rewards(
        self, labels=labels, 
        responses=all_responses, check_responses=check_responses, version_responses=version_responses,
        check_ids=check_ids)
    bt.logging.info("Miner uids: {}".format(miner_uids))
    bt.logging.info("Rewards: {}".format(rewards))
    bt.logging.info("Metrics: {}".format(metrics))

    rewards_tensor = torch.tensor(rewards).to(self.device)

    m = torch.nn.Softmax()
    rewards_tensor = m(rewards_tensor * 4)

    bt.logging.info("Normalized rewards: {}".format(rewards_tensor))

    uids_tensor = torch.tensor(miner_uids).to(self.device)
    self.update_scores(rewards_tensor, uids_tensor)

    self.log_step(miner_uids, metrics, rewards)
