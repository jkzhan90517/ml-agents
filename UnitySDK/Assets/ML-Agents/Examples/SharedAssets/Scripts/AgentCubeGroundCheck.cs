using System.Collections;
using UnityEngine;
// using MLAgents;

namespace MLAgents
{

    /// <summary>
    /// Perform Groundcheck using a Physics OverlapBox
    /// </summary>
    [DisallowMultipleComponent]
    public class AgentCubeGroundCheck : MonoBehaviour
    {
        public bool debugDrawGizmos;
        // public List<string> tagsToDetect = new List<string>(){"walkableSurface", "block"};
        public Collider[] hitGroundColliders = new Collider[3];

        public Vector3 groundCheckBoxLocalPos = new Vector3(0,-0.52f, 0);
        public Vector3 groundCheckBoxSize = new Vector3(0.99f, 0.02f, 0.99f);
        public bool isGrounded;
        public float ungroundedTime; //amount of time agent hasn't been grounded


        void FixedUpdate()
        {
            DoGroundCheck();
            if(!isGrounded)
            {
                ungroundedTime += Time.deltaTime;
            }
            else
            {
                ungroundedTime = 0;
            }
        }

        /// <summary>
        /// Does the ground check.
        /// </summary>
        /// <returns><c>true</c>, if the agent is on the ground,
        /// <c>false</c> otherwise.</returns>
        /// <param name="smallCheck"></param>
        public void DoGroundCheck()
        {
            // hitGroundColliders = new Collider[3];
            isGrounded = false;
            if(Physics.OverlapBoxNonAlloc(
                transform.TransformPoint(groundCheckBoxLocalPos),
                groundCheckBoxSize/2,
                hitGroundColliders,
                transform.rotation) > 0)
                {
                    foreach (var col in hitGroundColliders)
                    {
                        // if (col != null && col.transform != transform &&
                        //     (col.CompareTag("walkableSurface") ||
                        //      col.CompareTag("block") ||
                        //      col.CompareTag("wall")))
                        // {
                        if (col != null && col.transform != transform &&
                            (col.CompareTag("walkableSurface") ||
                            // col.CompareTag("wall") ||
                                col.CompareTag("block")))
                        {
                            isGrounded = true; //then we're grounded
                            break;
                        }
                    }
                }
            //empty the array
            for (int i = 0; i < hitGroundColliders.Length; i++)
            {
                hitGroundColliders[i] = null;
            }
        }

        //Draw the Box Overlap as a gizmo to show where it currently is testing. Click the Gizmos button to see this
        void OnDrawGizmos()
        {
            if (debugDrawGizmos)
            {
                // Convert the local coordinate values into world
                // coordinates for the matrix transformation.
                //Draw a cube where the OverlapBox is (positioned where your GameObject is as well as a size)
                // Gizmos.DrawWireCube(transform.position, transform.localScale);

                Gizmos.color = Color.red;
                Gizmos.matrix = transform.localToWorldMatrix;
                Gizmos.DrawWireCube(groundCheckBoxLocalPos, groundCheckBoxSize);
                // Gizmos.color = Color.blue;
                // Gizmos.DrawWireCube(transform.TransformPoint(groundCheckBoxLocalPos), groundCheckBoxSize);

                // Gizmos.DrawWireCube(transform.TransformPoint(groundCheckBoxLocalPos), transform.localScale);
            }
        }

    }
}