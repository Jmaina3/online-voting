from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

class Election:
    def __init__(self, name):
        self.name = name
        self.candidates = []

    def add_candidate(self, candidate):
        self.candidates.append(candidate)

class Candidate:
    def __init__(self, name, photo):
        self.name = name
        self.photo = self.save_photo(photo)
        self.votes = 0

    def save_photo(self, photo):
        candidates_dir = os.path.join(os.getcwd(), 'static', 'candidates')
        os.makedirs(candidates_dir, exist_ok=True)
        photo_path = os.path.join(candidates_dir, f"{self.name.lower().replace(' ', '_')}.jpg")
        photo.save(photo_path)
        return f"candidates/{self.name.lower().replace(' ', '_')}.jpg"

    def receive_vote(self):
        self.votes += 1

class Voter:
    def __init__(self, voter_id):
        self.voter_id = voter_id
        self.has_voted = False

    def cast_vote(self, candidate):
        if not self.has_voted:
            candidate.receive_vote()
            self.has_voted = True
            return True
        return False

class VotingSystem:
    def __init__(self):
        self.voters = []
        self.election = None

    def initiate_election(self, name):
        self.election = Election(name)

    def submit_candidates(self, candidate1_name, candidate1_photo, candidate2_name, candidate2_photo):
        candidate1 = Candidate(candidate1_name, candidate1_photo)
        candidate2 = Candidate(candidate2_name, candidate2_photo)
        self.election.add_candidate(candidate1)
        self.election.add_candidate(candidate2)
        return candidate1, candidate2

    def register_voters(self, voter_ids):
        for voter_id in voter_ids:
            self.voters.append(Voter(voter_id))

voting_system = VotingSystem()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/initiate_election', methods=['POST'])
def initiate_election():
    election_name = request.form['election_name']
    voting_system.initiate_election(election_name)
    return redirect(url_for('election'))

@app.route('/election')
def election():
    if not voting_system.election:
        return redirect(url_for('index'))
    return render_template('election.html', election=voting_system.election)

@app.route('/submit_candidates', methods=['POST'])
def submit_candidates():
    try:
        candidate1_name = request.form['candidate1_name']
        candidate1_photo = request.files['candidate1_photo']
        
        candidate2_name = request.form['candidate2_name']
        candidate2_photo = request.files['candidate2_photo']

        if candidate1_name and candidate1_photo and candidate2_name and candidate2_photo:
            candidate1, candidate2 = voting_system.submit_candidates(candidate1_name, candidate1_photo, candidate2_name, candidate2_photo)

            voter_ids = [1, 2, 3, 4, 5]
            voting_system.register_voters(voter_ids)

            return redirect(url_for('cast_vote'))
        else:
            raise ValueError("Form data incomplete")
    except Exception as e:
        print(f"Error submitting candidates: {str(e)}")
        return redirect(url_for('election'))  # Redirect to election page or handle error gracefully

@app.route('/cast_vote')
def cast_vote():
    if not voting_system.election:
        return redirect(url_for('index'))
    candidates = voting_system.election.candidates
    return render_template('cast_vote.html', candidates=candidates)


@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    voter_id = int(request.form['voter_id'])
    candidate_id = int(request.form['candidate'])
    voter = next((v for v in voting_system.voters if v.voter_id == voter_id), None)
    if voter and not voter.has_voted:
        voter.cast_vote(voting_system.election.candidates[candidate_id])
        return redirect(url_for('results'))  # Redirect to results page after successful vote
    return redirect(url_for('cast_vote'))  # Redirect to cast_vote page if vote submission fails


@app.route('/results')
def results():
    if not voting_system.election:
        return redirect(url_for('index'))
    candidates = voting_system.election.candidates
    total_votes = sum(candidate.votes for candidate in candidates)
    return render_template('results.html', candidates=candidates, total_votes=total_votes)

if __name__ == '__main__':
    app.run(debug=True)
