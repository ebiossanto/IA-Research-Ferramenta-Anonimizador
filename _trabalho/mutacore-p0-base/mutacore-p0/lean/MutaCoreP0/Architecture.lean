namespace MutaCoreP0
universe u v w
variable {State : Type u} {Action : Type v} {Certificate : Type w}
variable (Invariant : State → Prop)
variable (realStep modelStep : State → Action → State → Prop)
variable (verify : Certificate → State → Action → Bool)
variable (recover : State → Action)

def ConservativeModel : Prop := ∀ s a s', realStep s a s' → modelStep s a s'
def ModelPreserves (s : State) (a : Action) : Prop := ∀ s', modelStep s a s' → Invariant s'
end MutaCoreP0
