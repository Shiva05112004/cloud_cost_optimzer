import { useEffect } from 'react'
import { getEC2Instances } from '../api/resources.api'
import useDashboardStore from '../store/useDashboardStore'
import ResourceTable from '../components/ResourcesTable'
import LoadingSpinner from '../components/LoadingSpinner'

export default function ResourcesPage() {
  const { instances, loading, setInstances, setLoading } = useDashboardStore()

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const res = await getEC2Instances()
        setInstances(res.data.instances || [])
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  return (
    <div>
      <h1 className="page-title">Resources</h1>
      <p className="page-sub">All EC2 instances in your connected AWS account</p>

      <div className="card">
        {loading
          ? <LoadingSpinner text="Fetching instances..." />
          : <ResourceTable instances={instances} />
        }
      </div>
    </div>
  )
}